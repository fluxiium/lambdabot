import shutil
from typing import List, Union
import lamdabotweb.settings as config
import discord
import requests
import os
from django.db.models import Q
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from discord import Message
from discord.ext import commands
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from tempfile import mkdtemp
from util import headers, struuid4, is_url
from memeviewer.models import Meem, MemeSourceImage, MemeImagePool, MemeTemplate, QueuedMemeImage
import logging


class CommandContext(models.Model):
    class Meta:
        abstract = True

    disabled_cmds = models.TextField(blank=True, default='')
    blacklisted = models.BooleanField(default=False)

    def toggle_command(self, cmd_name, enable):
        disabled_cmds = self.disabled_cmds.strip().split()
        if enable is True and cmd_name in disabled_cmds:
            disabled_cmds.remove(cmd_name)
        elif enable is False and cmd_name not in disabled_cmds:
            disabled_cmds.append(cmd_name)
        self.disabled_cmds = ' '.join(disabled_cmds)
        self.save()

    def command_enabled(self, cmd_name):
        return cmd_name not in self.disabled_cmds.strip().split()


class DiscordServer(CommandContext):
    class Meta:
        verbose_name = 'Server'
        indexes = [models.Index(fields=['name'], name='idx_ds_name')]

    server_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=512, blank=True, default='')
    prefix = models.CharField(max_length=16, default='!')

    def __str__(self):
        return self.name or "?"


class DiscordChannel(CommandContext):
    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx_dc_name'),
            models.Index(fields=['server'], name='idx_dc_server'),
        ]

    channel_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    server = models.ForeignKey(DiscordServer, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    name = models.CharField(max_length=512, blank=True, default='')
    image_pools = models.ManyToManyField(MemeImagePool)
    submission_pool = models.ForeignKey(MemeImagePool, null=True, blank=True, default=None, on_delete=models.SET_NULL,
                                        related_name='submission_channel')
    recent_template = models.ForeignKey(MemeTemplate, null=True, default=None, on_delete=models.SET_NULL)
    recent_image = models.TextField(blank=True, default='')
    discord_users = models.ManyToManyField('DiscordUser', through='DiscordChannelUser')

    def __str__(self):

        return f'#{self.name or "?"} ({self.server})'


@receiver(m2m_changed, sender=DiscordChannel.image_pools.through)
def pools_changed(sender, instance, **_):
    if isinstance(instance, DiscordChannel):
        QueuedMemeImage.objects.filter(queue_id='dc-' + str(instance.channel_id)).delete()


@receiver(post_save, sender=DiscordChannel)
def channel_saved(sender, instance: DiscordChannel, created, **_):
    if created:
        try:
            hlpool = MemeImagePool.objects.get(name='halflife')
            templpool = MemeImagePool.objects.get(name='templates')
            instance.image_pools.add(hlpool)
            instance.image_pools.add(templpool)
            instance.submission_pool = hlpool
            instance.save()
        except MemeImagePool.DoesNotExist:
            pass


class DiscordUser(models.Model):

    class Meta:
        indexes = [models.Index(fields=['name'], name='idx_du_name')]

    user_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=512, blank=True, default='')
    blacklisted = models.BooleanField(default=False)

    def available_pools(self, channel_data: Union[DiscordChannel, List[DiscordChannel]]=None):
        if isinstance(channel_data, DiscordChannel):
            channel_data = [channel_data]
        avail = MemeImagePool.objects.filter(Q(memeimagepoolownership=None) | Q(memeimagepoolownership__status=POOL_PUBLIC) | Q(memeimagepoolownership__owner=self) | Q(memeimagepoolownership__shared_with=self))
        if channel_data:
            channel_avail = MemeImagePool.objects.filter(Q(discordchannel__in=channel_data) | Q(pk__in=map(lambda c: c.submission_pool.pk, channel_data)))
            avail = MemeImagePool.objects.filter(Q(pk__in=avail.values_list('pk', flat=True)) | Q(pk__in=channel_avail.values_list('pk', flat=True)))
        return avail

    @property
    def moderated_pools(self):
        return MemeImagePool.objects.filter(Q(memeimagepoolownership__owner=self) | Q(memeimagepoolownership__moderators=self))

    @transaction.atomic
    def generate_meme(self, channel: DiscordChannel, template: MemeTemplate):
        meme = Meem.generate(channel.image_pools.all(), 'dc-' + str(channel.channel_id), template)
        channel.recent_template = meme.template_link
        channel.save()
        discord_meme = DiscordMeem.objects.create(meme=meme, discord_user=self, discord_channel=channel)
        return discord_meme

    def __str__(self):
        return self.name or "?"


class DiscordChannelUser(models.Model):
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)
    discord_channel = models.ForeignKey(DiscordChannel, on_delete=models.CASCADE)


POOL_PRIVATE = 0
POOL_PENDING = 1
POOL_REJECTED = 2
POOL_PUBLIC = 3
POOL_STATUS = (
    (POOL_PRIVATE, 'Private'),
    (POOL_PENDING, 'Pending approval'),
    (POOL_REJECTED, 'Private (Rejected)'),
    (POOL_PUBLIC, 'Public'),
)

class MemeImagePoolOwnership(models.Model):
    class Meta:
        indexes = []

    owner = models.ForeignKey(DiscordUser, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    image_pool = models.OneToOneField(MemeImagePool, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(DiscordUser, blank=True, related_name='shared_image_pool')
    moderators = models.ManyToManyField(DiscordUser, blank=True, related_name='moderated_image_pool')
    status = models.IntegerField(choices=POOL_STATUS, default=POOL_PRIVATE)

    def __str__(self):
        return f'{self.owner} ({self.get_status_display()})'


class DiscordSourceImgSubmission(models.Model):
    sourceimg = models.ForeignKey(MemeSourceImage, on_delete=models.CASCADE)
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.SET_NULL, null=True, default=None)
    discord_channel = models.ForeignKey(DiscordChannel, on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return str(self.sourceimg)


class DiscordMeem(models.Model):
    meme = models.OneToOneField(Meem, on_delete=models.CASCADE)
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.SET_NULL, null=True, default=None)
    discord_channel = models.ForeignKey(DiscordChannel, on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return str(self.meme)


class DiscordContext(commands.Context):
    __images = None
    __is_manager = None
    __server_data = None
    __channel_data = None
    __user_data = None

    @property
    def is_manager(self):
        if self.__is_manager is None:
            self.__is_manager = getattr(self.channel.permissions_for(self.author), 'manage_guild', None) or self.author.id == 257499042039332866
        return self.__is_manager

    @property
    def is_blacklisted(self):
        return self.user_data.blacklisted or (self.channel_data and self.channel_data.blacklisted) or (self.server_data and self.server_data.blacklisted)

    @property
    def server_data(self):
        if not self.guild:
            return None
        if self.__server_data is None:
            self.__server_data = DiscordServer.objects.update_or_create(server_id=str(self.guild.id), defaults={
                'name': self.guild.name
            })[0]
        return self.__server_data

    @property
    def channel_data(self):
        if self.__channel_data is None:
            self.__channel_data = DiscordChannel.objects.update_or_create(channel_id=str(self.channel.id), defaults={
                'name': self.guild and self.channel.name or 'DM-' + str(self.channel.id),
                'server': self.server_data
            })[0]
            DiscordChannelUser.objects.get_or_create(discord_channel=self.__channel_data, discord_user=self.user_data)
        return self.__channel_data

    @property
    def user_data(self):
        if self.__user_data is None:
            self.__user_data = DiscordUser.objects.update_or_create(user_id=str(self.author.id), defaults={
                'name': self.author.name
            })[0]
        return self.__user_data

    @property
    def can_respond(self):
        return getattr(self.channel.permissions_for(self.guild and self.guild.me or self.bot.user), 'send_messages', None)

    @property
    def images(self):
        if self.__images:
            return self.__images
        self.__images = DiscordImage.from_message(self.message)
        return self.__images


class DiscordImage:
    def __init__(self, url, filename=None):
        self.url = url
        self.filename = filename
        self.tmpdir = None

    @classmethod
    def from_message(cls, msg: Message, attachments_only=False, just_one=False):
        images = {}
        for attachment in msg.attachments:
            images[attachment.proxy_url] = attachment.filename
        if not attachments_only:
            for embed in msg.embeds:
                if embed.image != discord.Embed.Empty and embed.image.url != discord.Embed.Empty:
                    images[embed.image.url] = None
                elif embed.thumbnail != discord.Embed.Empty and embed.thumbnail.url != discord.Embed.Empty:
                    images[embed.thumbnail.url] = None
            for url in msg.content.split(' '):
                url = url.strip('<>')
                if is_url(url):
                    images[url] = None
        actual_images = []
        for url, filename in images.items():
            try:
                r = requests.head(url, headers=headers)
            except (ValueError, requests.exceptions.ConnectionError):
                continue
            contenttype = r.headers.get('content-type')
            contentlength = r.headers.get('content-length')
            if contenttype and 'image' in contenttype and contentlength and int(contentlength) <= config.MAX_SRCIMG_SIZE:
                actual_images.append(cls(url, filename or struuid4()))
                if just_one and len(actual_images) == 1:
                    return actual_images[0]
        if not attachments_only and len(actual_images) == 0:  # get last image from channel
            try:
                channel_data = DiscordChannel.objects.get(channel_id=msg.channel.id)
                if channel_data.recent_image:
                    actual_images.append(cls(channel_data.recent_image, struuid4()))
            except DiscordChannel.DoesNotExist:
                pass
        if just_one:
            return len(actual_images) > 0 and actual_images[0] or None
        else:
            return actual_images

    def save(self, filename_override=None):
        self.tmpdir = mkdtemp(prefix="lambdabot_attach_")
        filename = os.path.join(self.tmpdir, filename_override or self.filename)
        url = self.url
        logging.info(f'saving image: {url} -> {filename}')
        attachment = requests.get(url, headers=headers)
        with open(filename, 'wb') as attachment_file:
            attachment_file.write(attachment.content)
        return filename

    def cleanup(self):
        shutil.rmtree(self.tmpdir)
        self.tmpdir = None
