import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import MemeContext, Meem
from discordbot.models import DiscordServer, DiscordUser, DiscordServerUser, DiscordMeem, DiscordSourceImgSubmission

for c in MemeContext.objects.all():
    memes = Meem.objects.filter(context_link=c)
    c.meme_count = memes.count()
    c.save()

for u in DiscordServerUser.objects.all():
    memes = DiscordMeem.objects.filter(server_user=u)
    u.meme_count = memes.count()
    subs = DiscordSourceImgSubmission.objects.filter(server_user=u)
    u.submission_count = subs.count()
    u.save()

for u in DiscordUser.objects.all():
    u.meme_count = 0
    u.submission_count = 0
    for su in u.discordserveruser_set.all():
        u.meme_count += su.meme_count
        u.submission_count += su.submission_count
    u.save()

for s in DiscordServer.objects.all():
    s.meme_count = 0
    s.submission_count = 0
    for su in s.discordserveruser_set.all():
        s.meme_count += su.meme_count
        s.submission_count += su.submission_count
    s.save()
