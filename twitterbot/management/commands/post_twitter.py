import twitter
from django.core.management import BaseCommand
from lamdabotweb.settings import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN_KEY, \
    TWITTER_ACCESS_TOKEN_SECRET
from memeviewer.models import MemeContext
from memeviewer.preview import preview_meme
from twitterbot.models import TwitterMeem


class Command(BaseCommand):
    help = 'Posts a meme to twitter'

    def handle(self, *args, **options):
        api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
                          consumer_secret=TWITTER_CONSUMER_SECRET,
                          access_token_key=TWITTER_ACCESS_TOKEN_KEY,
                          access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)

        meme = MemeContext.by_id_or_create('twitter', 'Twitter', is_public=True).generate()
        preview_meme(meme)

        status = api.PostUpdate(
            meme.get_info_url(),
            media=open(meme.get_local_path(), 'rb')
        )
        print("post added!")
        print(status)

        TwitterMeem.objects.create(meme=meme, post=status.id)
