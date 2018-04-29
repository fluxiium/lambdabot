from django.core.management import BaseCommand
from twitterbot.models import TwitterPage


class Command(BaseCommand):
    help = 'Posts a meme to twitter'

    def handle(self, *args, **options):
        for p in TwitterPage.objects.all():
            p.generate_meme()
