from django.core.management import BaseCommand

from memeviewer.models import MemeImagePool, Meem


class Command(BaseCommand):
    help = 'Generate a meme'

    def add_arguments(self, parser):
        parser.add_argument('pool', nargs='*')

    def handle(self, *args, **options):
        pools = MemeImagePool.objects.filter(name__in=options['pool'])
        meme = Meem.generate(pools, 'default')
        meme.make_img().show()
