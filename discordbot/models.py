import shutil
import config
import discord
import requests
import os
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from discord import Message
from discord.ext import commands
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from tempfile import mkdtemp
from util import log, headers, struuid4, is_url
from memeviewer.models import Meem, MemeSourceImage, MemeImagePool, MemeTemplate, QueuedMemeImage


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
    name = models.CharField(max_length=64, blank=True, default='')
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
    name = models.CharField(max_length=64, blank=True, default='')
    image_pools = models.ManyToManyField(MemeImagePool)
    submission_pool = models.ForeignKey(MemeImagePool, null=True, blank=True, default=None, on_delete=models.SET_NULL,
                                        related_name='submission_channel')
    recent_template = models.ForeignKey(MemeTemplate, null=True, default=None, on_delete=models.SET_NULL)
    recent_image = models.TextField(blank=True, default='')

    def __str__(self):
        return '#{0} ({1})'.format(self.name or '?', self.server)


@receiver(m2m_changed, sender=DiscordChannel.image_pools.through)
def pools_changed(sender, instance, **_):
    if isinstance(instance, DiscordChannel):
        QueuedMemeImage.objects.filter(queue_id='dc-' + instance.channel_id).delete()


class DiscordUser(models.Model):

    class Meta:
        indexes = [models.Index(fields=['name'], name='idx_du_name')]

    user_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=64, blank=True, default='')
    blacklisted = models.BooleanField(default=False)

    @property
    def available_pools(self):
        return MemeImagePool.objects.filter(Q(memeimagepoolownership=None) | Q(memeimagepoolownership__owner=self) | Q(memeimagepoolownership__shared_with=self))

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

    @transaction.atomic
    def submit_sourceimg(self, channel: DiscordChannel, path, filename=None):
        submission = MemeSourceImage.submit(channel.submission_pool, path, filename)
        return DiscordSourceImgSubmission.objects.create(sourceimg=submission, discord_user=self, discord_channel=channel)

    def __str__(self):
        return self.name or "?"


class MemeImagePoolOwnership(models.Model):
    class Meta:
        indexes = []

    owner = models.ForeignKey(DiscordUser, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    image_pool = models.OneToOneField(MemeImagePool, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(DiscordUser, blank=True, related_name='shared_image_pool')
    moderators = models.ManyToManyField(DiscordUser, blank=True, related_name='moderated_image_pool')
    publish_requested = models.BooleanField(default=False)

    def __str__(self):
        return str(self.owner)


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

    @property
    def server_data(self):
        if not self.guild:
            return None
        server, cr = DiscordServer.objects.get_or_create(server_id=self.guild.id, defaults={'name': self.guild.name})
        if not cr and not server.name:
            server.name = self.guild.name
            server.save()
        return server

    @property
    def channel_data(self):
        if not getattr(self.channel.permissions_for(self.guild and self.guild.me or self.bot.user), 'send_messages', None):
            return None
        chname = self.guild and self.channel.name or 'DM-' + str(self.channel.id)
        channel, cr = DiscordChannel.objects.get_or_create(channel_id=self.channel.id, defaults={'name': chname})
        if not cr:
            if not channel.name:
                channel.name = chname
                channel.save()
            if self.guild and not channel.server:
                channel.server = self.server_data
                channel.save()
        return channel

    @property
    def user_data(self):
        user, cr = DiscordUser.objects.get_or_create(user_id=self.author.id, defaults={'name': self.author.name})
        if not cr and not user.name:
            user.name = self.author.name
            user.save()
        return user

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
    def from_message(cls, msg: Message, attachments_only=False):
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
            except ValueError:
                continue
            contenttype = r.headers.get('content-type')
            contentlength = r.headers.get('content-length')
            if contenttype and 'image' in contenttype and contentlength and int(contentlength) <= config.MAX_SRCIMG_SIZE:
                actual_images.append(cls(url, filename or struuid4()))
        if not attachments_only and len(actual_images) == 0:  # get last image from channel
            try:
                channel_data = DiscordChannel.objects.get(channel_id=msg.channel.id)
                if channel_data.recent_image:
                    actual_images.append(cls(channel_data.recent_image, struuid4()))
            except DiscordChannel.DoesNotExist:
                pass
        return actual_images

    def save(self, filename_override=None):
        self.tmpdir = mkdtemp(prefix="lambdabot_attach_")
        filename = os.path.join(self.tmpdir, filename_override or self.filename)
        url = self.url
        log('saving image: {0} -> {1}'.format(url, filename))
        attachment = requests.get(url, headers=headers)
        with open(filename, 'wb') as attachment_file:
            attachment_file.write(attachment.content)
        return filename

    def cleanup(self):
        shutil.rmtree(self.tmpdir)
        self.tmpdir = None
