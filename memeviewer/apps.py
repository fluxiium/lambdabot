from django.apps import AppConfig
from lamdabotweb.settings import BOT_NAME


class MemeviewerConfig(AppConfig):
    name = 'memeviewer'
    verbose_name = BOT_NAME + ' Core'
