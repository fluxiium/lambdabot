import re
import os
from django.core.management import BaseCommand
from lamdabotweb.settings import MEDIA_ROOT
from memeviewer.models import MemeSourceImage, MemeImagePool

IMPORT_DIR = os.path.join(MEDIA_ROOT, 'sourceimg', 'manual')
ALLOWED_EXTENSIONS = r'.*\.jpg|.*\.jpeg|.*\.png|.*\.webp|.*\.gif'


class Command(BaseCommand):
    help = 'Import source images from disk (MEDIA_SUBDIR/sourceimg/manual)'

    def add_arguments(self, parser):
        parser.add_argument('pool')

    def handle(self, *args, **options):
        os.makedirs(IMPORT_DIR, exist_ok=True)
        pool = MemeImagePool.objects.get(name=options['pool'])
        for file in os.listdir(IMPORT_DIR):
            if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
                print(file)
                img = MemeSourceImage.submit(pool, os.path.join(IMPORT_DIR, file), file)
                img.accepted = True
                img.save()
                os.remove(os.path.join(IMPORT_DIR, file))
