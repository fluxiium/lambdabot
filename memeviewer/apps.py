import os
from django.apps import AppConfig
from lamdabotweb.settings import MEDIA_ROOT, MEDIA_SUBDIR


class MemeviewerConfig(AppConfig):
    name = 'memeviewer'
    verbose_name = 'Meme generator'

    def ready(self):
        os.makedirs(os.path.join(MEDIA_ROOT, MEDIA_SUBDIR, 'memes'), exist_ok=True)
        os.makedirs(os.path.join(MEDIA_ROOT, MEDIA_SUBDIR, 'sourceimg'), exist_ok=True)
        os.makedirs(os.path.join(MEDIA_ROOT, MEDIA_SUBDIR, 'templates'), exist_ok=True)
