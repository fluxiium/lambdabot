import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import MemeTemplate


ts = MemeTemplate.objects.filter(memetemplateslot__mask=False).distinct()

for t in ts:
    for s in t.memetemplateslot_set.all():
        if s.mask:
            continue
    t.bg_image_file = t.image_file
    t.image_file = None
    t.save()

print(ts.count())
