import re
import os
from django.core.management import BaseCommand
from lamdabotweb.settings import MEDIA_ROOT
from memeviewer.models import MemeSourceImage, MemeContext

IMPORT_DIR = os.path.join(MEDIA_ROOT, 'sourceimg', 'manual')
ALLOWED_EXTENSIONS = r'.*\.jpg|.*\.jpeg|.*\.png|.*\.webp|.*\.gif'


class Command(BaseCommand):
    help = 'Import source images from disk (MEDIA_SUBDIR/sourceimg/manual)'

    def add_arguments(self, parser):
        parser.add_argument('context', nargs='*')

    def handle(self, *args, **options):
        os.makedirs(IMPORT_DIR, exist_ok=True)
        ctxs = []
        for ctxname in options['context']:
            ctxs.append(MemeContext.objects.get(short_name=ctxname))
        for file in os.listdir(IMPORT_DIR):
            if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
                print(file)
                img = MemeSourceImage.submit(os.path.join(IMPORT_DIR, file), file)
                for ctx in ctxs:
                    img.contexts.add(ctx)
                img.accepted = True
                img.save()
                os.remove(os.path.join(IMPORT_DIR, file))
