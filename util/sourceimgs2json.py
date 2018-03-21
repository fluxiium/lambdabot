import django
import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem, MemeSourceImageInSlot

n = 0

for m in Meem.objects.all().order_by('number'):
    if m.number - n > 100:
        n = m.number
        print(n)
    imgsinslots = MemeSourceImageInSlot.objects.filter(meme=m).order_by('slot__slot_order')
    imgs = {}
    for img in imgsinslots:
        if img.slot.slot_order not in imgs:
            imgs[img.slot.slot_order] = img.source_image.name
    m.source_images = json.dumps(imgs)
    m.save()
