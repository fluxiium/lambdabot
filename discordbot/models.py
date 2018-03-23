from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from memeviewer.models import MemeContext, Meem, MemeSourceImage


class DiscordServer(models.Model):

    class Meta:
        verbose_name = "Discord server"

    server_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name="Server name", blank=True, default='')
    context = models.ForeignKey(MemeContext, verbose_name='Context', on_delete=models.CASCADE)
    prefix = models.CharField(max_length=8, default='!', verbose_name='Prefix')

    meme_limit_count = models.IntegerField(default=3, verbose_name='Meme limit')
    meme_limit_time = models.IntegerField(default=10, verbose_name='Meme limit cooldown')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')

    @classmethod
    def get_by_id(cls, server_id):
        return cls.objects.filter(server_id=server_id).first()

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    def get_commands(self):
        return DiscordCommand.objects.filter(server=self).order_by('cmd')

    def get_cmd(self, cmd):
        return self.get_commands().filter(cmd=cmd).first()

    def update(self, name):
        self.name = name
        self.save()

    def add_meem(self):
        self.meme_count += 1
        self.save()
        self.context.add_meem()

    def add_sourceimg_submission(self):
        self.submission_count += 1
        self.save()

    def __str__(self):
        return str(self.name)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.server_id,))


class DiscordCommand(models.Model):

    class Meta:
        verbose_name = "Command"

    cmd = models.CharField(max_length=32, primary_key=True, verbose_name='Command')
    message = models.TextField(blank=True, default='', verbose_name='Text message')
    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, verbose_name="Server")

    def __str__(self):
        return self.cmd


class DiscordUser(models.Model):

    class Meta:
        verbose_name = "Discord user"

    user_id = models.CharField(max_length=64, verbose_name='User ID', primary_key=True)
    name = models.CharField(max_length=64, verbose_name='Username')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')

    def update(self, name):
        self.name = name
        self.save()

    def add_meem(self):
        self.meme_count += 1
        self.save()

    def add_sourceimg_submission(self):
        self.submission_count += 1
        self.save()

    def __str__(self):
        return str(self.name)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.user_id,))

    def get_srcimg_admin_url(self):
        content_type = ContentType.objects.get_for_model(MemeSourceImage)
        return reverse("admin:%s_%s_changelist" % (content_type.app_label, content_type.model)) + \
            "?discordsourceimgsubmission__server_user__user__user_id__exact=" + self.user_id


class DiscordServerUser(models.Model):

    class Meta:
        verbose_name = "Server user"
        unique_together = ('user', 'server')

    user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, verbose_name="Discord user")
    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, verbose_name="Server")
    nickname = models.CharField(max_length=64, verbose_name='Nickname', blank=True, default='')
    unlimited_memes = models.BooleanField(default=False, verbose_name='Unlimited memes')

    submission_count = models.IntegerField(default=0, verbose_name='Submitted source images')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')

    @classmethod
    def get_by_id(cls, user_id, server):
        server_user = DiscordServerUser.objects.filter(user__user_id=user_id, server=server).first()
        if server_user is None:
            user = DiscordUser.objects.filter(user_id=user_id).first()
            if user is None:
                user = DiscordUser(user_id=user_id)
                user.save()
            server_user = DiscordServerUser(user=user, server=server)
            server_user.save()
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
        self.user.add_meem()
        self.server.add_meem()
        return discord_meme

    def submit_sourceimg(self, path, filename=None):
        submission = MemeSourceImage.submit(path, filename)
        if submission is None:
            return None
        discord_submission = DiscordSourceImgSubmission.objects.create(server_user=self, sourceimg=submission)
        self.submission_count += 1
        self.save()
        self.user.add_sourceimg_submission()
        self.server.add_sourceimg_submission()
        return discord_submission

    def update(self, nickname):
        self.nickname = nickname
        self.save()

    def __str__(self):
        return "{0} ({1})".format(self.nickname, self.server)


class DiscordSourceImgSubmission(models.Model):
    server_user = models.ForeignKey(DiscordServerUser, null=True, on_delete=models.CASCADE)
    sourceimg = models.ForeignKey(MemeSourceImage, on_delete=models.CASCADE)

    def __str__(self):
        return "{0} ({1})".format(self.sourceimg, self.server_user)


class DiscordMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    server_user = models.ForeignKey(DiscordServerUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    channel_id = models.CharField(max_length=32)

    def __str__(self):
        return "{0} ({1})".format(self.meme.meme_id, self.server_user)
