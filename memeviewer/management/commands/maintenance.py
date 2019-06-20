import os
import re
from django.db.models import Q
from datetime import timedelta
from django.core.management import BaseCommand
from django.utils import timezone
from memeviewer.models import Meem, MemeSourceImage, MemeTemplate, MemeImagePool
from memeviewer import settings


class Command(BaseCommand):
    help = 'Do some maintenance work'

    def handle(self, *args, **options):

        # delete meme images generated >MEEM_CLEANUP_DAYS days ago

        for m in Meem.objects.filter(gen_date__lte=timezone.now() - timedelta(days=settings.MEEM_CLEANUP_DAYS)):
            try:
                os.remove(m.local_path)
            except FileNotFoundError:
                pass

        # delete orphaned sourceimg/template files

        sourceimg_dir = os.path.join(settings.MEDIA_ROOT, 'sourceimg')
        template_dir = os.path.join(settings.MEDIA_ROOT, 'templates')
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

        # update meme image quartiles

        def update_quartiles(imset):
            # exclude the top 5% of items to remove outliers
            clean_imset = imset.exclude(name__in=imset.order_by('-random_usages')[:int(imset.count() * 0.05)].values_list('name', flat=True))
            try:
                mx = clean_imset.latest('random_usages').random_usages
                mn = clean_imset.earliest('random_usages').random_usages
            except (MemeSourceImage.DoesNotExist, MemeTemplate.DoesNotExist):
                return
            q1 = int(mn + (mx - mn) * 0.25)
            q2 = int(mn + (mx - mn) * 0.5)
            q3 = int(mn + (mx - mn) * 0.75)
            imset.filter(random_usages__lt=q1).update(quartile=1)
            imset.filter(random_usages__gte=q1, random_usages__lt=q2).update(quartile=2)
            imset.filter(random_usages__gte=q2, random_usages__lt=q3).update(quartile=3)
            imset.filter(random_usages__gte=q3).update(quartile=4)

        for p in MemeImagePool.objects.all():
            update_quartiles(p.memesourceimage_set.filter(accepted=True))
            update_quartiles(p.memetemplate_set.filter(accepted=True))
