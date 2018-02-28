# adds a bunch of source images to the database

import os
import django
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from lamdabotweb.settings import MEDIA_ROOT, MEDIA_SUBDIR
from memeviewer.models import MemeSourceImage

ALLOWED_EXTENSIONS = r'.*\.jpg|.*\.jpeg|.*\.png'
SOURCEIMG_DIR = os.path.join(MEDIA_ROOT, MEDIA_SUBDIR, 'sourceimg')

imgdir = os.path.join(SOURCEIMG_DIR, "manual")
os.makedirs(imgdir, exist_ok=True)

for file in os.listdir(imgdir):
    if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
        print(file)
        img = MemeSourceImage.submit(os.path.join(imgdir, file), file)
        img.accepted = True
        img.save()
        os.remove(os.path.join(imgdir, file))
