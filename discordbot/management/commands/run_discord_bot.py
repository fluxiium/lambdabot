from django.core.management import BaseCommand
from discordbot.bot import run_bot

class Command(BaseCommand):
    help = 'Starts discord bot'

    def handle(self, *args, **options):
        run_bot()
