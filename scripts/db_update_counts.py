import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import MemeContext, Meem, MemeTemplate, MemeSourceImage
from discordbot.models import DiscordServer, DiscordUser, DiscordServerUser

for c in MemeContext.objects.all():
    c.meme_count = c.meem_set.count()
    c.save()

for u in DiscordServerUser.objects.all():
    u.meme_count = u.discordmeem_set.count()
    u.submission_count = u.discordsourceimgsubmission_set.count()
    u.save()

for u in DiscordUser.objects.all():
    u.meme_count = 0
    u.submission_count = 0
    u.server_count = u.discordserveruser_set.count()
    for su in u.discordserveruser_set.all():
        u.meme_count += su.meme_count
        u.submission_count += su.submission_count
    u.save()

for s in DiscordServer.objects.all():
    s.meme_count = 0
    s.submission_count = 0
    s.user_count = s.discordserveruser_set.count()
    for su in s.discordserveruser_set.all():
        s.meme_count += su.meme_count
        s.submission_count += su.submission_count
    s.save()

for m in MemeTemplate.objects.all():
    m.meme_count = m.meem_set.count()
    m.save()

for i in MemeSourceImage.objects.all():
    i.meme_count = Meem.objects.filter(source_images__contains='"%s"' % i.name).count()
    i.save()
