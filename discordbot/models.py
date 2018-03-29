import discord
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from typing import Union

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

    meme_limit_count = models.IntegerField(default=3, verbose_name='Meme limit')
    meme_limit_time = models.IntegerField(default=10, verbose_name='Meme limit cooldown')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')
    user_count = models.IntegerField(default=0, verbose_name='Users')

    def update(self, name=None):
        self.name = name
        self.save()

    @classmethod
    def get(cls, discord_server: discord.Guild):
        return cls.objects.get(server_id=discord_server.id)

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

    def _add_meem(self):
        self.meme_count += 1
        self.save()
        self.context._add_meem()

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
    unlimited_memes = models.BooleanField(default=False, verbose_name='Unlimited memes')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')

    def update(self, discord_user: Union[discord.Member, discord.User]):
        self.user.name = discord_user.name
        self.user.save()

    def get_meme_limit(self):
        limit_count = self.server.meme_limit_count
        limit_time = self.server.meme_limit_time
        seconds_left = 0
        if not self.unlimited_memes:
            since = timezone.now() - timedelta(minutes=limit_time)
            memes = DiscordMeem.objects.filter(server_user=self, meme__gen_date__gte=since).order_by('-meme__gen_date')[:limit_count]
            if limit_count <= memes.count():
                seconds_left = int((memes[limit_count - 1].meme.gen_date - since).total_seconds()) + 1
        return seconds_left, limit_count, limit_time

    def generate_meme(self, template, channel):
        meme = self.server.context.generate(template=template)
        discord_meme = DiscordMeem.objects.create(meme=meme, server_user=self, channel_id=channel.id)
        self.meme_count += 1
        self.save()
        self.user._add_meem()
        self.server._add_meem()
        return discord_meme

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
