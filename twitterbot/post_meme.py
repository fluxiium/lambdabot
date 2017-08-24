import os
import django
import twitter

from lamdabotweb.settings import DATA_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem, TwitterMeem
from memeviewer.preview import preview_meme

token_file = open(os.path.join(DATA_DIR, 'twittertokens.txt'), 'r')
TOKENS = token_file.read().splitlines()
token_file.close()

api = twitter.Api(consumer_key=TOKENS[0],
                  consumer_secret=TOKENS[1],
                  access_token_key=TOKENS[2],
                  access_token_secret=TOKENS[3])

meme = Meem.generate(context='twitter')
preview_meme(meme)

status = api.PostUpdate(
    meme.get_info_url(),
    media=open(meme.get_local_path(), 'rb')
)
print("post added!")
print(status)

twitter_meme = TwitterMeem(meme=meme, post=status.id)
twitter_meme.save()
