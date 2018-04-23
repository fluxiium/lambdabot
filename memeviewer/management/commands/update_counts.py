from django.core.management import BaseCommand
from memeviewer.models import MemeContext, Meem, MemeTemplate, MemeSourceImage
from discordbot.models import DiscordServer, DiscordUser, DiscordServerUser, DiscordMeem, DiscordSourceImgSubmission


class Command(BaseCommand):
    help = 'Re-calculates values of counter fields in the database'

    def handle(self, *args, **options):
        for c in MemeContext.objects.all():
            c.meme_count = c.meem_set.count()
            c.save()

        for u in DiscordUser.objects.all():
            u.meme_count = 0
            u.submission_count = 0
            u.server_count = u.discordserveruser_set.count()
            u.meme_count = u.discordmeem_set.count()
            u.submission_count = u.discordsourceimgsubmission_set.count()
            u.save()

        for s in DiscordServer.objects.all():
            s.meme_count = 0
            s.submission_count = 0
            s.user_count = s.discordserveruser_set.count()
            s.meme_count = s.discordmeem_set.count()
            s.submission_count = s.discordsourceimgsubmission_set.count()
            s.save()
            for su in s.discordserveruser_set.all():
                su.meme_count = DiscordMeem.objects.filter(discord_server=s, discord_user=su.user).count()
                su.submission_count = DiscordSourceImgSubmission.objects.filter(discord_server=s, discord_user=su.user).count()

        for m in MemeTemplate.objects.all():
            m.meme_count = m.meem_set.count()
            m.save()

        for i in MemeSourceImage.objects.all():
            i.meme_count = Meem.objects.filter(source_images__contains='"%s"' % i.name).count()
            i.save()
