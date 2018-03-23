from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from memeviewer.models import MemeContext, Meem, MemeSourceImage


# noinspection PyProtectedMember
class DiscordServer(models.Model):

    class Meta:
        verbose_name = "Discord server"

    server_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name="Server name", blank=True, default='')
    context = models.ForeignKey(MemeContext, verbose_name='Context', default='default', on_delete=models.SET_DEFAULT)
    prefix = models.CharField(max_length=8, default='!', verbose_name='Prefix')

    meme_limit_count = models.IntegerField(default=3, verbose_name='Meme limit')
    meme_limit_time = models.IntegerField(default=10, verbose_name='Meme limit cooldown')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')
    user_count = models.IntegerField(default=0, verbose_name='Users')

    @classmethod
    def update(cls, server_id, name=None):
        server = cls.objects.filter(server_id=server_id).first()
        if name is not None:
            server.name = name
            server.save()
        return server

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    def get_commands(self):
        return DiscordCommand.objects.filter(server=self).order_by('cmd')

    def get_cmd(self, cmd):
        return self.get_commands().filter(cmd=cmd).first()

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

    cmd = models.CharField(max_length=32, primary_key=True, verbose_name='Command')
    message = models.TextField(blank=True, default='', verbose_name='Text message')
    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, verbose_name="Server")

    def __str__(self):
        return "{0} ({1})".format(self.cmd, self.server)


class DiscordUser(models.Model):

    class Meta:
        verbose_name = "Discord user"

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

    user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, verbose_name="Discord user")
    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, verbose_name="Server")
    unlimited_memes = models.BooleanField(default=False, verbose_name='Unlimited memes')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')

    @classmethod
    def update(cls, user_id, server, name=None):
        user, _ = DiscordUser.objects.get_or_create(user_id=user_id)
        if name is not None:
            user.name = name
            user.save()
        server_user, created = DiscordServerUser.objects.get_or_create(user=user, server=server)
        if created:
            server._add_user()
            user._add_server()
        return server_user

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
        meme = Meem.generate(context=self.server.context, template=template)
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


class DiscordMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    server_user = models.ForeignKey(DiscordServerUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    channel_id = models.CharField(max_length=32)
