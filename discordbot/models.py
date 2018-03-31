import discord
import requests
import uuid
from datetime import timedelta
from discord.ext import commands
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils import timezone
from tempfile import mkdtemp
from typing import Union

import os

from discordbot.util import log, headers
from memeviewer.models import MemeContext, Meem, MemeSourceImage


# noinspection PyProtectedMember
class DiscordServer(models.Model):

    class Meta:
        verbose_name = "Discord server"
        indexes = [
            models.Index(fields=['context'], name='idx_ds_context'),
            models.Index(fields=['name'], name='idx_ds_name'),
            models.Index(fields=['submission_count'], name='idx_ds_scount'),
            models.Index(fields=['meme_count'], name='idx_ds_mcount'),
        ]

    server_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name="Server name", blank=True, default='')
    context = models.ForeignKey(MemeContext, verbose_name='Context', default='default', on_delete=models.SET_DEFAULT)
    prefix = models.CharField(max_length=8, default='!', verbose_name='Prefix')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')
    user_count = models.IntegerField(default=0, verbose_name='Users')

    def update(self, name=None):
        self.name = name
        self.save()

    @classmethod
    def get(cls, discord_server: discord.Guild, create=False):
        if not create:
            return cls.objects.get(server_id=discord_server.id)
        else:
            context = MemeContext.by_id_or_create('default', 'Default')
            return cls.objects.get_or_create(server_id=discord_server.id, defaults={
                'name': discord_server.name,
                'context': context,
            })[0]

    def get_commands(self):
        return DiscordCommand.objects.filter(server=self).order_by('cmd')

    def get_cmd(self, cmd):
        return self.get_commands().filter(cmd=cmd).first()

    def get_member(self, discord_user: Union[discord.Member, discord.User], create=False):
        if not create:
            return DiscordServerUser.objects.get(user_id=discord_user.id, server=self)
        else:
            user, _ = DiscordUser.objects.get_or_create(user_id=discord_user.id, defaults={'name': discord_user.name})
            member, created = DiscordServerUser.objects.get_or_create(user=user, server=self)
            if created:
                self._add_user()
                user._add_server()
            return member

    def _add_meem(self):
        self.meme_count += 1
        self.save()

    def _add_sourceimg_submission(self):
        self.submission_count += 1
        self.save()

    def _add_user(self):
        self.user_count += 1
        self.save()

    def __str__(self):
        return self.name or "?"


class DiscordCommand(models.Model):

    class Meta:
        verbose_name = "Command"
        unique_together = ('server', 'cmd')
        indexes = [
            models.Index(fields=['server', 'cmd'], name='idx_discordcmd')
        ]

    cmd = models.CharField(max_length=32, verbose_name='Command')
    message = models.TextField(blank=True, default='', verbose_name='Text message')
    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, verbose_name="Server")

    def __str__(self):
        return "{0} ({1})".format(self.cmd, self.server)


class DiscordUser(models.Model):

    class Meta:
        verbose_name = "Discord user"
        indexes = [
            models.Index(fields=['name'], name='idx_du_name'),
            models.Index(fields=['submission_count'], name='idx_du_scount'),
            models.Index(fields=['meme_count'], name='idx_du_mcount'),
        ]

    user_id = models.CharField(max_length=64, verbose_name='User ID', primary_key=True)
    name = models.CharField(max_length=64, verbose_name='Username')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')
    server_count = models.IntegerField(default=0, verbose_name='Servers')

    def update(self, name):
        self.name = name
        self.save()

    def _add_meem(self):
        self.meme_count += 1
        self.save()

    def _add_sourceimg_submission(self):
        self.submission_count += 1
        self.save()

    def _add_server(self):
        self.server_count += 1
        self.save()

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

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')

    def update(self, discord_user: Union[discord.Member, discord.User]):
        self.user.name = discord_user.name
        self.user.save()

    @transaction.atomic
    def generate_meme(self, template, channel):
        meme = self.server.context.generate(template=template)
        discord_meme = DiscordMeem.objects.create(meme=meme, server_user=self, channel_id=channel.id)
        self.meme_count += 1
        self.save()
        self.user._add_meem()
        self.server._add_meem()
        return discord_meme

    @transaction.atomic
    def submit_sourceimg(self, path, filename=None):
        submission = MemeSourceImage.submit(path, filename)
        if submission is None:
            return None
        discord_submission = DiscordSourceImgSubmission.objects.create(server_user=self, sourceimg=submission)
        self.submission_count += 1
        self.save()
        self.user._add_sourceimg_submission()
        self.server._add_sourceimg_submission()
        return discord_submission

    def __str__(self):
        return "{0} ({1})".format(self.user, self.server)


class DiscordSourceImgSubmission(models.Model):
    server_user = models.ForeignKey(DiscordServerUser, null=True, on_delete=models.CASCADE)
    sourceimg = models.ForeignKey(MemeSourceImage, on_delete=models.CASCADE)

    def __str__(self):
        return "{} ({})".format(self.sourceimg, self.server_user)


class DiscordMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    server_user = models.ForeignKey(DiscordServerUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    channel_id = models.CharField(max_length=32)

    def __str__(self):
        return "{} ({})".format(self.meme, self.server_user)


class DiscordContext(commands.Context):
    @property
    def server_data(self):
        return DiscordServer.get(self.guild, create=True)

    @property
    def member_data(self):
        return self.server_data.get_member(self.message.author, create=True)


class DiscordImage:
    def __init__(self, att, is_embed):
        self.__att = att
        self.is_embed = is_embed
        if self.is_embed:
            self.filename = str(uuid.uuid4())
            self.url = self.__att
        else:
            self.filename = self.__att.filename
            self.url = self.__att.proxy_url

    @classmethod
    def get_from_message(cls, msg: discord.Message, get_embeds=True):
        images = []
        for att in msg.attachments:
            images.append(cls.__from_attachment(att))
        if not get_embeds:
            return images
        for emb in msg.embeds:
            try:
                images.append(cls.__from_embed(emb))
            except AttributeError:
                pass
        return images

    @classmethod
    def __from_embed(cls, embed: discord.Embed):
        if embed.image != discord.Embed.Empty and embed.image.url != discord.Embed.Empty:
            return cls(embed.image.url, True)
        elif embed.thumbnail != discord.Embed.Empty and embed.thumbnail.url != discord.Embed.Empty:
            return cls(embed.thumbnail.url, True)
        else:
            raise AttributeError

    @classmethod
    def __from_attachment(cls, attachment: discord.Attachment):
        return cls(attachment, False)

    def save(self):
        tmpdir = mkdtemp(prefix="lambdabot_attach_")
        filename = os.path.join(tmpdir, self.filename)
        url = self.url
        log('saving image: {0} -> {1}'.format(url, filename))
        attachment = requests.get(url, headers=headers)
        with open(filename, 'wb') as attachment_file:
            attachment_file.write(attachment.content)
        return filename
