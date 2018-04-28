import shutil
import config
import discord
import requests
import os
from discord import Message
from discord.ext import commands
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from tempfile import mkdtemp
from util import log, headers, struuid4, is_url
from memeviewer.models import Meem, MemeSourceImage, MemeImagePool, MemeTemplate


class DiscordServer(models.Model):
    class Meta:
        verbose_name = 'Server'
        indexes = [models.Index(fields=['name'], name='idx_ds_name')]

    server_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, blank=True, default='')
    blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return self.name or "?"


class DiscordChannel(models.Model):
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
    blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return '#{0} ({1})'.format(self.name or '?', self.server)


class DiscordUser(models.Model):

    class Meta:
        indexes = [models.Index(fields=['name'], name='idx_du_name')]

    user_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=64, blank=True, default='')
    blacklisted = models.BooleanField(default=False)

    @transaction.atomic
    def generate_meme(self, channel: DiscordChannel, template: MemeTemplate):
        meme = Meem.generate(channel.image_pools.all(), 'dc-' + channel.channel_id, template)
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
    __server_data = None
    __channel_data = None
    __user_data = None

    @property
    def server_data(self):
        if not self.guild:
            return None
        if self.__server_data:
            return self.__server_data
        server, cr = DiscordServer.objects.get_or_create(server_id=self.guild.id, defaults={'name': self.guild.name})
        if not cr and not server.name:
            server.name = self.guild.name
            server.save()
        self.__server_data = server
        return server

    @property
    def channel_data(self):
        if self.__channel_data:
            return self.__channel_data
        chname = self.guild and self.channel.name or 'DM-' + str(self.channel.id)
        channel, cr = DiscordChannel.objects.get_or_create(channel_id=self.channel.id, defaults={'name': chname})
        if not cr:
            if not channel.name:
                channel.name = chname
                channel.save()
            if self.guild and not channel.server:
                channel.server = self.server_data
                channel.save()
        self.__channel_data = channel
        return channel

    @property
    def user_data(self):
        if self.__user_data:
            return self.__user_data
        user, cr = DiscordUser.objects.get_or_create(user_id=self.author.id, defaults={'name': self.author.name})
        if not cr and not user.name:
            user.name = self.author.name
            user.save()
        self.__user_data = user
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
            r = requests.head(url, headers=headers)
            contenttype = r.headers.get('content-type')
            contentlength = int(r.headers.get('content-length'))
            if 'image' in contenttype and contentlength <= config.MAX_SRCIMG_SIZE:
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
