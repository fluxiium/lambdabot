from django.core.management import BaseCommand
from facebookbot.models import FacebookPage


class Command(BaseCommand):
    help = 'Posts a meme to facebook'

    def handle(self, *args, **options):
        for p in FacebookPage.objects.all():
            p.generate_meme()
