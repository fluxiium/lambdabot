import datetime
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

    submit_limit_count = models.IntegerField(default=10, verbose_name='Submission limit')
    submit_limit_time = models.IntegerField(default=300, verbose_name='Submission limit cooldown')

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

    def update(self, name):
        self.name = name
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

    meme_limit_count = models.IntegerField(verbose_name='Meme limit', default=None, null=True, blank=True)
    meme_limit_time = models.IntegerField(verbose_name='Meme limit timeout', default=None, null=True, blank=True)

    submit_limit_count = models.IntegerField(verbose_name='Submission limit', default=None, null=True, blank=True)
    submit_limit_time = models.IntegerField(verbose_name='Submission limit timeout', default=None, null=True, blank=True)

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

    def get_memes(self, limit=None):
        memes = DiscordMeem.objects.filter(server_user=self).order_by('-meme__gen_date')
        if limit is not None:
            memes = memes[:limit]
        return memes

    def get_submits(self, limit=None):
        memes = DiscordSourceImgSubmission.objects.filter(server_user=self).order_by('-sourceimg__add_date')
        if limit is not None:
            memes = memes[:limit]
        return memes

    def get_meme_limit(self):
        return (
            self.server.meme_limit_count if self.meme_limit_count is None else self.meme_limit_count,
            self.server.meme_limit_time if self.meme_limit_time is None else self.meme_limit_time,
        )

    def get_submit_limit(self):
        return (
            self.server.submit_limit_count if self.submit_limit_count is None else self.submit_limit_count,
            self.server.submit_limit_time if self.submit_limit_time is None else self.submit_limit_time,
        )

    def update(self, nickname):
        self.nickname = nickname
        self.save()

    def __str__(self):
        return "{0} ({1})".format(self.nickname, self.server)

    def get_memes_admin_url(self):
        content_type = ContentType.objects.get_for_model(Meem)
        return reverse("admin:%s_%s_changelist" % (content_type.app_label, content_type.model)) + \
            "?discordmeem__server_user__user__user_id__exact=" + self.user.user_id + \
            "&discordmeem__server_user__server__server_id__exact=" + self.server.server_id


class DiscordSourceImgSubmission(models.Model):
    class Meta:
        verbose_name = "Discord source image submission"

    server_user = models.ForeignKey(DiscordServerUser, null=True, on_delete=models.SET_NULL, verbose_name="Server user")
    sourceimg = models.ForeignKey(MemeSourceImage, on_delete=models.CASCADE, verbose_name="Source image")

    def __str__(self):
        return "{0} ({1})".format(self.sourceimg, self.server_user)


class DiscordMeem(models.Model):

    class Meta:
        verbose_name = "Discord meme link"

    meme = models.ForeignKey(Meem, on_delete=models.CASCADE, verbose_name='Meme link')
    server_user = models.ForeignKey(DiscordServerUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    channel_id = models.CharField(max_length=32)

    def __str__(self):
        return "{0} ({1})".format(self.meme.meme_id, self.server_user)


class MurphyRequest(models.Model):

    class Meta:
        verbose_name = "Murphy bot request"

    question = models.CharField(max_length=256, blank=True, default='', verbose_name="Question")
    face_pic = models.CharField(max_length=256, blank=True, default='', verbose_name="Face pic")
    server_user = models.ForeignKey(DiscordServerUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    ask_date = models.DateTimeField(default=timezone.now, verbose_name='Date asked')
    channel_id = models.CharField(max_length=32, verbose_name="Discord channel ID")
    processed = models.BooleanField(default=False, verbose_name="Processed?")

    @classmethod
    def ask(cls, server_user, channel_id, question='', face_pic=''):
        request = cls(question=question, server_user=server_user, channel_id=channel_id, face_pic=face_pic)
        request.save()
        return request

    @classmethod
    def get_next_unprocessed(cls, minutes=None):
        requests = cls.objects.filter(processed=False)
        if minutes is not None:
            requests = requests.filter(ask_date__gte=(timezone.now() - datetime.timedelta(minutes=minutes)))
        return requests.order_by('ask_date').first()

    def mark_processed(self):
        self.processed = True
        self.save()

    def __str__(self):
        if self.face_pic is not None and self.question is not None:
            rstr = "{0} ({1})".format(self.question, self.face_pic)
        elif self.question is not None:
            rstr = self.question
        else:
            rstr = self.face_pic
        return "{0} ({1})".format(rstr, self.server_user)


class MurphyFacePic(models.Model):

    class Meta:
        verbose_name = "Murphy bot face pic"

    channel_id = models.CharField(max_length=32, primary_key=True, verbose_name="Discord channel ID")
    face_pic = models.CharField(max_length=256, blank=True, default='', verbose_name="Face pic")
    last_used = models.DateTimeField(default=timezone.now, verbose_name='Last used')

    @classmethod
    def set(cls, channel_id, face_pic=None):
        face_pic_data = cls.objects.filter(channel_id=channel_id).first()
        if face_pic_data is None:
            face_pic_data = cls(channel_id=channel_id, face_pic=face_pic)
        elif face_pic is not None:
            face_pic_data.face_pic = face_pic
        face_pic_data.last_used = timezone.now()
        face_pic_data.save()

    @classmethod
    def get(cls, channel_id):
        face_pic_data = cls.objects.filter(channel_id=channel_id).first()
        return face_pic_data.face_pic if face_pic_data is not None else None

    @classmethod
    def get_last_used(cls):
        face_pic_data = cls.objects.order_by('-last_used').first()
        return face_pic_data.face_pic if face_pic_data is not None else None

    def __str__(self):
        return self.channel_id


class ProcessedMessage(models.Model):

    class Meta:
        verbose_name = "Processed message"

    msg_id = models.CharField(max_length=32, verbose_name="Message ID")
    process_date = models.DateTimeField(default=timezone.now, verbose_name='Date processed')

    @classmethod
    def was_id_processed(cls, msg_id):
        return cls.objects.filter(msg_id=msg_id).first() is not None

    @classmethod
    def process_id(cls, msg_id):
        if cls.objects.filter(msg_id=msg_id).first() is None:
            cls(msg_id=msg_id).save()
