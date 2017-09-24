import datetime

from django.db import models
from django.utils import timezone

from memeviewer.models import MemeContext, Meem


class DiscordServer(models.Model):

    class Meta:
        verbose_name = "Server"

    server_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name="Server name", null=True, blank=True, default=None)
    context = models.ForeignKey(MemeContext, verbose_name='Context')
    prefix = models.CharField(max_length=8, default='!', verbose_name='Prefix')
    meme_limit_count = models.IntegerField(default=3, verbose_name='Meme limit')
    meme_limit_time = models.IntegerField(default=10, verbose_name='Meme limit cooldown')

    @classmethod
    def get_by_id(cls, server_id):
        return cls.objects.filter(server_id=server_id).first()

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    def update(self, name):
        self.name = name
        self.save()

    def __str__(self):
        return str(self.name)


class DiscordCommand(models.Model):

    class Meta:
        verbose_name = "Command"

    cmd = models.CharField(max_length=32, primary_key=True, verbose_name='Command')
    help = models.TextField(null=True, blank=True, verbose_name='Help string')
    message = models.TextField(null=True, blank=True, verbose_name='Text message')
    hidden = models.BooleanField(default=False)
    restricted = models.BooleanField(default=False)

    def check_permission(self, member):
        allow = member.check_permission("cmd_{0}".format(self.cmd))
        return allow if allow is not None else not self.restricted

    @classmethod
    def get_cmd(cls, cmd):
        return cls.objects.filter(cmd__iexact=cmd).first()

    def __str__(self):
        return self.cmd


class DiscordServerPermission(models.Model):

    class Meta:
        verbose_name = "Server permission"

    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, verbose_name="Server")
    permission = models.CharField(max_length=64, verbose_name="Permission")
    allow = models.BooleanField(default=True, verbose_name="Allow")


class DiscordUser(models.Model):

    class Meta:
        verbose_name = "User"

    user_id = models.CharField(max_length=64, verbose_name='User ID', primary_key=True)
    name = models.CharField(max_length=64, verbose_name='Username')

    def update(self, name):
        self.name = name
        self.save()

    def __str__(self):
        return str(self.name)


class DiscordServerUser(models.Model):

    class Meta:
        verbose_name = "Server user"
        unique_together = ('user', 'server')

    user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, verbose_name="Discord user")
    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE, verbose_name="Server")
    nickname = models.CharField(max_length=64, verbose_name='Nickname', null=True, blank=True, default=None)
    meme_limit_count = models.IntegerField(verbose_name='Meme limit', default=None, null=True, blank=True)
    meme_limit_time = models.IntegerField(verbose_name='Meme limit timeout', default=None, null=True, blank=True)

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

    def get_meme_limit(self):
        return (
            self.server.meme_limit_count if self.meme_limit_count is None else self.meme_limit_count,
            self.server.meme_limit_time if self.meme_limit_time is None else self.meme_limit_time,
        )

    def get_commands(self):
        cmds = DiscordCommand.objects.order_by('cmd')
        result = []
        for cmd in cmds:
            if cmd.check_permission(self):
                result.append(cmd)
        return result

    def check_permission(self, permission):
        perm_data = DiscordServerUserPermission.objects.filter(server_user=self, permission=permission).first()
        if perm_data:
            return perm_data.allow
        perm_data = DiscordServerPermission.objects.filter(server=self.server, permission=permission).first()
        if perm_data:
            return perm_data.allow
        else:
            return None  # TODO: change when added roles

    def update(self, nickname):
        self.nickname = nickname
        self.save()

    def __str__(self):
        return "{0} ({1})".format(self.nickname, self.server)


class DiscordServerUserPermission(models.Model):

    class Meta:
        verbose_name = "Server user permission"
        unique_together = ('server_user', 'permission')

    server_user = models.ForeignKey(DiscordServerUser, on_delete=models.CASCADE, verbose_name="Server user")
    permission = models.CharField(max_length=64, verbose_name="Permission")
    allow = models.BooleanField(default=True, verbose_name="Allow")


class DiscordMeem(models.Model):

    class Meta:
        verbose_name = "Discord meme link"

    meme = models.ForeignKey(Meem, on_delete=models.CASCADE, verbose_name='Meme link')
    server_user = models.ForeignKey(DiscordServerUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    channel_id = models.CharField(max_length=32)
    sent_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name='Date sent')

    @classmethod
    def get_next_unsent(cls):
        return cls.objects.filter(sent_date__isnull=True).order_by('meme__gen_date').first()

    def mark_sent(self):
        self.sent_date = timezone.now()
        self.save()

    def __str__(self):
        return "{0} ({1})".format(self.meme.meme_id, self.server_user)


class MurphyRequest(models.Model):

    class Meta:
        verbose_name = "Murphy bot request"

    request = models.CharField(max_length=256, verbose_name="Request")
    server_user = models.ForeignKey(DiscordServerUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    ask_date = models.DateTimeField(default=timezone.now, verbose_name='Date asked')
    process_date = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Process start')
    answer_date = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Date answered')
    channel_id = models.CharField(max_length=32)
    accept_date = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Date accepted')
    related_request = models.ForeignKey('self', on_delete=models.SET_NULL, default=None, null=True, blank=True, verbose_name='Related request')

    @classmethod
    def ask(cls, question, server_user, channel_id, related_request=None):
        request = cls(request=question, server_user=server_user, channel_id=channel_id, related_request=related_request)
        request.save()
        return request

    @classmethod
    def get_next(cls, minutes=None):
        requests = cls.objects.filter(process_date__isnull=True)
        if minutes is not None:
            requests = requests.filter(ask_date__gte=(timezone.now() - datetime.timedelta(minutes=minutes)))
        return requests.order_by('ask_date').first()

    def start_process(self):
        self.process_date = timezone.now()
        self.save()

    def accept(self):
        self.accept_date = timezone.now()
        self.save()

    def mark_processed(self):
        self.answer_date = timezone.now()
        self.save()

    def is_i_pic_request(self):
        return self.request.startswith("ipic:")

    def __str__(self):
        return "{0} ({1})".format(self.request.split('\n', 1)[0], self.server_user)


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
        cls(msg_id=msg_id).save()
