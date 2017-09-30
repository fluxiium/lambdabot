import os
import django
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from lamdabotweb.settings import SOURCEIMG_DIR, ALLOWED_EXTENSIONS
from memeviewer.models import MemeSourceImage, MemeContext

imgdir = os.path.join(SOURCEIMG_DIR, "manual")
os.makedirs(imgdir, exist_ok=True)
deldir = os.path.join(SOURCEIMG_DIR, "deleted")
os.makedirs(deldir, exist_ok=True)

context = input("Context? (empty for any)\n")
if context == "":
    context = None
else:
    context = MemeContext.objects.get(short_name=context)

for file in os.listdir(imgdir):
    if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
        print(file)
        img = MemeSourceImage.submit(os.path.join(imgdir, file))
        img.friendly_name = file
        if context is not None:
            img.contexts.add(context)
        img.save()
        os.rename(os.path.join(imgdir, file), os.path.join(deldir, file))
