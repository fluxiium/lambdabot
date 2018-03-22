# this script generates one meme and posts it to a twitter page

import os
import django
import twitter

from lamdabotweb.settings import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN_KEY, \
    TWITTER_ACCESS_TOKEN_SECRET

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem, MemeContext
from memeviewer.preview import preview_meme
from twitterbot.models import TwitterMeem

api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
                  consumer_secret=TWITTER_CONSUMER_SECRET,
                  access_token_key=TWITTER_ACCESS_TOKEN_KEY,
                  access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)

meme = Meem.generate(context=MemeContext.by_id_or_create('twitter', 'Twitter', is_public=True))
preview_meme(meme)

status = api.PostUpdate(
    meme.get_info_url(),
    media=open(meme.get_local_path(), 'rb')
)
print("post added!")
print(status)

twitter_meme = TwitterMeem.objects.create(meme=meme, post=status.id)
