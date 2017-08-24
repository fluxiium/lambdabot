import os
import django
import twitter

from lamdabotweb.settings import DATA_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem
from memeviewer.preview import preview_meme

token_file = open(os.path.join(DATA_DIR, 'twittertokens.txt'), 'r')
TOKENS = token_file.read().splitlines()
token_file.close()

api = twitter.Api(consumer_key=TOKENS[0],
                  consumer_secret=TOKENS[1],
                  access_token_key=TOKENS[2],
                  access_token_secret=TOKENS[3])

meme = Meem.generate(context='facebook')
preview_meme(meme)

status = api.PostUpdate(
    "https://lambdabot.morchkovalski.com/meme_info/" + meme.meme_id,
    media=open(meme.get_local_path(), 'rb')
)
print("post added!")
print(status.id)
