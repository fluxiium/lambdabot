import config
import discord
import requests
import os

from discord import Message
from discord.ext import commands
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from tempfile import mkdtemp
from typing import Union
from util import log, headers, struuid4, is_url
from memeviewer.models import MemeContext, Meem, MemeSourceImage, MemeImagePool, MemeTemplate


class DiscordServer(models.Model):
    class Meta:
        indexes = [models.Index(fields=['name'], name='idx_ds_name')]

    server_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, blank=True, default='')
    context = models.ForeignKey(MemeContext, verbose_name='Context', default='default', on_delete=models.SET_DEFAULT)
    blacklisted = models.BooleanField(default=False)

    def get_member_data(self, discord_user: Union[discord.Member, discord.User]):
        user = DiscordUser.get(discord_user)
        return DiscordServerUser.objects.get_or_create(user=user, server=self)[0]

    def __str__(self):
        return self.name or "?"


class DiscordChannel(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx_dc_name'),
            models.Index(fields=['server'], name='idx_dc_server'),
        ]

    server = models.ForeignKey(DiscordServer, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    name = models.CharField(max_length=64, blank=True, default='')
    image_pools = models.ManyToManyField(MemeImagePool)
    last_template = models.ForeignKey(MemeTemplate, null=True, default=None, on_delete=models.SET_NULL)
    last_image = models.TextField(blank=True, default='')
    blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return self.name or "?"


class DiscordUser(models.Model):

    class Meta:
        indexes = [models.Index(fields=['name'], name='idx_du_name')]

    user_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=64, blank=True, default='')
    blacklisted = models.BooleanField(default=False)

    @transaction.atomic
    def generate_meme(self, template, channel):
        # todo: pass pools instead of context
        meme = MemeContext.by_id_or_create('discorddm', 'Discord DM').generate(template=template)
        discord_meme = DiscordMeem.objects.create(meme=meme, discord_user=self, channel_id=channel.id)
        return discord_meme

    @transaction.atomic
    def submit_sourceimg(self, path, filename=None):
        submission = MemeSourceImage.submit(path, filename)
        if submission is None:
            return None
        return DiscordSourceImgSubmission.objects.create(sourceimg=submission, discord_user=self)

    def __str__(self):
        return self.name or "?"


# noinspection PyProtectedMember
class DiscordServerUser(models.Model):

    class Meta:
        verbose_name = "Server user"
        unique_together = ('user', 'server')
        indexes = [
            models.Index(fields=['user', 'server'], name='idx_ds_user'),
        ]

    user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, verbose_name="Discord user")
    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, verbose_name="Server")
    blacklisted = models.BooleanField(default=False)

    def update(self, discord_user: Union[discord.Member, discord.User]):
        self.user.name = discord_user.name
        self.user.save()

    @transaction.atomic
    def generate_meme(self, template, channel):
        meme = self.server.context.generate(template=template)
        return DiscordMeem.objects.create(meme=meme, discord_server=self.server, discord_user=self.user, channel_id=channel.id)

    @transaction.atomic
    def submit_sourceimg(self, path, filename=None):
        submission = MemeSourceImage.submit(path, filename)
        if submission is None:
            return None
        return DiscordSourceImgSubmission.objects.create(sourceimg=submission, discord_server=self.server, discord_user=self.user)

    def __str__(self):
        return "{0} ({1})".format(self.user, self.server)


class DiscordSourceImgSubmission(models.Model):
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, null=True, default=None)
    discord_server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, null=True, default=None)
    sourceimg = models.ForeignKey(MemeSourceImage, on_delete=models.CASCADE)


class DiscordMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.SET_NULL, null=True, default=None)
    discord_server = models.ForeignKey(DiscordServer, on_delete=models.SET_NULL, null=True, default=None)
    channel_id = models.CharField(max_length=32, null=True, default=None)
    # todo: migrate channel_id+discord_server -> channel
    discord_channel = models.ForeignKey(DiscordChannel, on_delete=models.SET_NULL, null=True, default=None)


class DiscordContext(commands.Context):
    __images = None

    @property
    def server_data(self):
        return self.guild and DiscordServer.get(self.guild) or None

    @property
    def user_data(self):
        return self.guild and self.server_data.get_member(self.message.author) or DiscordUser.get(self.message.author)

    @property
    def images(self):
        if self.__images is None:
            self.__images = DiscordImage.from_message(self.message)
        return self.__images


class DiscordImage:
    channel_recents = {}

    def __init__(self, url, filename=None):
        self.url = url
        self.filename = filename

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
        recent = cls.channel_recents.get(msg.channel)
        if not attachments_only and len(actual_images) == 0 and recent:
            actual_images.append(recent)
        return actual_images

    @classmethod
    def update_channel_recent(cls, ctx: DiscordContext):
        if len(ctx.images) > 0:
            cls.channel_recents[ctx.channel] = ctx.images[0]

    def save(self, filename_override=None):
        tmpdir = mkdtemp(prefix="lambdabot_attach_")
        filename = os.path.join(tmpdir, filename_override or self.filename)
        url = self.url
        log('saving image: {0} -> {1}'.format(url, filename))
        attachment = requests.get(url, headers=headers)
        with open(filename, 'wb') as attachment_file:
            attachment_file.write(attachment.content)
        return filename
