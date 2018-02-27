import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import MemeTemplate, MemeSourceImage


for t in MemeTemplate.objects.all():
    t.image_file = 'lambdabot/templates/' + t.name
    if t.bg_img:
        t.bg_image_file = 'lambdabot/templates/' + t.bg_img
    t.save()

for t in MemeSourceImage.objects.all():
    t.image_file = 'lambdabot/sourceimg/' + t.name
    t.save()
