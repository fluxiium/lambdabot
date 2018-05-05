import re
import os
from django.core.management import BaseCommand
from memeviewer.models import MemeSourceImage, MemeImagePool
import lamdabotweb.settings as config

ALLOWED_EXTENSIONS = r'.*\.jpg|.*\.jpeg|.*\.png|.*\.webp|.*\.gif'


class Command(BaseCommand):
    help = 'Import source images from disk'

    def add_arguments(self, parser):
        parser.add_argument('pool')

    def handle(self, *args, **options):
        pool = MemeImagePool.objects.get(name=options['pool'])
        sourceimg_dir = os.path.join(config.MEDIA_ROOT, 'sourceimg')
        for file in os.listdir(sourceimg_dir):
            if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
                try:
                    MemeSourceImage.objects.get(image_file='sourceimg/' + file)
                except MemeSourceImage.DoesNotExist:
                    print(file)
                    MemeSourceImage.objects.create(image_pool=pool, friendly_name=file, image_file='sourceimg/' + file)
