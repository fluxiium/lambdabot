import os
from django.apps import AppConfig
from lamdabotweb.settings import MEDIA_ROOT


class MemeviewerConfig(AppConfig):
    name = 'memeviewer'
    verbose_name = 'Meme generator'

    def ready(self):
        os.makedirs(os.path.join(MEDIA_ROOT, 'memes'), exist_ok=True)
        os.makedirs(os.path.join(MEDIA_ROOT, 'sourceimg'), exist_ok=True)
        os.makedirs(os.path.join(MEDIA_ROOT, 'templates'), exist_ok=True)
