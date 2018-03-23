# this script moves all images that are not associated with a source image or template object in the database
# into a directory called "deleted"

import os
import django
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from lamdabotweb.settings import MEDIA_SUBDIR, MEDIA_ROOT
from memeviewer.models import MemeSourceImage, MemeTemplate

ALLOWED_EXTENSIONS = r'.*\.jpg|.*\.jpeg|.*\.png'

print('source images --------------------------')

SOURCEIMG_DIR = os.path.join(MEDIA_ROOT, MEDIA_SUBDIR, 'sourceimg')
deldir = os.path.join(SOURCEIMG_DIR, "deleted")
os.makedirs(deldir, exist_ok=True)

for file in os.listdir(SOURCEIMG_DIR):
    if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
        img = MemeSourceImage.objects.filter(image_file=MEDIA_SUBDIR + '/sourceimg/' + file).first()
        if img is None:
            print(file)
            os.rename(os.path.join(SOURCEIMG_DIR, file), os.path.join(deldir, file))

print('templates --------------------------')

TEMPLATE_DIR = os.path.join(MEDIA_ROOT, MEDIA_SUBDIR, 'templates')
deldir = os.path.join(TEMPLATE_DIR, "deleted")
os.makedirs(deldir, exist_ok=True)

for file in os.listdir(TEMPLATE_DIR):
    if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
        img = MemeTemplate.objects.filter(image_file=MEDIA_SUBDIR + '/templates/' + file).first()
        if img is None:
            print(file)
            os.rename(os.path.join(TEMPLATE_DIR, file), os.path.join(deldir, file))
