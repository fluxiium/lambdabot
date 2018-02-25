# adds a bunch of source images to the database

import os
import django
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from lamdabotweb.settings import SOURCEIMG_DIR
from memeviewer.models import MemeSourceImage

ALLOWED_EXTENSIONS = r'.*\.jpg|.*\.jpeg|.*\.png'

imgdir = os.path.join(SOURCEIMG_DIR, "manual")
os.makedirs(imgdir, exist_ok=True)

for file in os.listdir(imgdir):
    if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
        print(file)
        img = MemeSourceImage.submit(os.path.join(imgdir, file), file)
        img.friendly_name = file
        img.accepted = True
        img.save()
        os.remove(os.path.join(imgdir, file))
