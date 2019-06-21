from django.core.management import BaseCommand
from facebookbot.models import FacebookPage


class Command(BaseCommand):
    help = 'Gets a permanent access token for your facebook page'

    def add_arguments(self, parser):
        parser.add_argument('page_id')
        parser.add_argument('temp_token')

    def handle(self, *args, **options):
        page_id = options['page_id']
        temp_token = options['temp_token']
        FacebookPage.objects.get(page_id=page_id).update_token(temp_token)
