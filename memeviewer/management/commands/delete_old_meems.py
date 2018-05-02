import os
from datetime import timedelta
from django.core.management import BaseCommand
from django.utils import timezone
from memeviewer.models import Meem


class Command(BaseCommand):
    help = 'Delete images of memes generated more than 30 days ago'

    def handle(self, *args, **options):
        for m in Meem.objects.filter(gen_date__lte=timezone.now() - timedelta(days=30)):
            try:
                os.remove(m.local_path)
            except FileNotFoundError:
                pass
