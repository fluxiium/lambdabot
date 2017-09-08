from django.db import models
from django.db.models import Q

from memeviewer.models import MemeContext, Meem


class DiscordServer(models.Model):

    class Meta:
        verbose_name = "Server"

    server_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
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

    def get_commands(self):
        return DiscordCommand.objects.filter(Q(server_whitelist=None) | Q(server_whitelist=self))

    def __str__(self):
        return "{0} - {1}".format(self.server_id, self.context)


class DiscordCommand(models.Model):

    class Meta:
        verbose_name = "Command"

    cmd = models.CharField(max_length=32, primary_key=True, verbose_name='Command')
    help = models.TextField(null=True, blank=True, verbose_name='Help string')
    server_whitelist = models.ManyToManyField(DiscordServer, blank=True, verbose_name='Server whitelist')
    message = models.TextField(null=True, blank=True, verbose_name='Text message')

    @classmethod
    def get_cmd(cls, cmd, server=None):
        result = cls.objects.filter(cmd=cmd)
        if server is not None:
            result = result.filter(Q(server_whitelist=None) | Q(server_whitelist=server))
        return result.first()

    def __str__(self):
        return self.cmd


class DiscordMeem(models.Model):

    class Meta:
        verbose_name = "Discord meme link"

    meme = models.ForeignKey(Meem, on_delete=models.CASCADE, verbose_name='Meme link')
    server = models.CharField(max_length=64, verbose_name='Server link')

    def __str__(self):
        return "{0} - {1}".format(self.meme.number, self.server)
