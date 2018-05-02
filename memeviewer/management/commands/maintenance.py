import os
import re
from django.db.models import Q
import lamdabotweb.settings as config
from datetime import timedelta
from django.core.management import BaseCommand
from django.utils import timezone
from memeviewer.models import Meem, MemeSourceImage, MemeTemplate


class Command(BaseCommand):
    help = 'Do some maintenance work'

    def handle(self, *args, **options):

        # delete meme images generated >MEEM_CLEANUP_DAYS days ago

        for m in Meem.objects.filter(gen_date__lte=timezone.now() - timedelta(days=config.MEEM_CLEANUP_DAYS)):
            try:
                os.remove(m.local_path)
            except FileNotFoundError:
                pass

        # delete orphaned sourceimg/template files

        sourceimg_dir = os.path.join(config.MEDIA_ROOT, 'sourceimg')
        template_dir = os.path.join(config.MEDIA_ROOT, 'templates')
        allowed_extensions = r'.*\.jpg|.*\.jpeg|.*\.png|.*\.webp|.*\.gif'

        deldir = os.path.join(sourceimg_dir, "deleted")
        os.makedirs(deldir, exist_ok=True)

        for file in os.listdir(sourceimg_dir):
            if re.match(allowed_extensions, file, re.IGNORECASE):
                try:
                    MemeSourceImage.objects.get(image_file='sourceimg/' + file)
                except MemeSourceImage.DoesNotExist:
                    os.rename(os.path.join(sourceimg_dir, file), os.path.join(deldir, file))

        deldir = os.path.join(template_dir, "deleted")
        os.makedirs(deldir, exist_ok=True)

        for file in os.listdir(template_dir):
            if re.match(allowed_extensions, file, re.IGNORECASE):
                try:
                    MemeTemplate.objects.get(Q(image_file='templates/' + file) | Q(bg_image_file='templates/' + file))
                except MemeTemplate.DoesNotExist:
                    os.rename(os.path.join(template_dir, file), os.path.join(deldir, file))
