import os
import re

from django.core.management import BaseCommand
from django.db.models import Q

from lamdabotweb.settings import MEDIA_ROOT
from memeviewer.models import MemeSourceImage, MemeTemplate

ALLOWED_EXTENSIONS = r'.*\.jpg|.*\.jpeg|.*\.png|.*\.webp|.*\.gif'
SOURCEIMG_DIR = os.path.join(MEDIA_ROOT, 'sourceimg')
TEMPLATE_DIR = os.path.join(MEDIA_ROOT, 'templates')


class Command(BaseCommand):
    help = 'Move all images that arent used as a source image or template to a directory called "deleted"'

    def handle(self, *args, **options):

        print('source images --------------------------')

        deldir = os.path.join(SOURCEIMG_DIR, "deleted")
        os.makedirs(deldir, exist_ok=True)

        for file in os.listdir(SOURCEIMG_DIR):
            if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
                try:
                    MemeSourceImage.objects.get(image_file='sourceimg/' + file)
                except MemeSourceImage.DoesNotExist:
                    print(file)
                    os.rename(os.path.join(SOURCEIMG_DIR, file), os.path.join(deldir, file))

        print('templates --------------------------')

        deldir = os.path.join(TEMPLATE_DIR, "deleted")
        os.makedirs(deldir, exist_ok=True)

        for file in os.listdir(TEMPLATE_DIR):
            if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
                try:
                    MemeTemplate.objects.get(Q(image_file='templates/' + file) | Q(bg_image_file='templates/' + file))
                except MemeTemplate.DoesNotExist:
                    print(file)
                    os.rename(os.path.join(TEMPLATE_DIR, file), os.path.join(deldir, file))
