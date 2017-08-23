import twitter

from lambdabot.preview import preview_meme
from lambdabot.db import make_meme
from lambdabot.settings import *

token_file = open(os.path.join(DATA_DIR, 'twittertokens.txt'), 'r')
TOKENS = token_file.read().splitlines()
token_file.close()

api = twitter.Api(consumer_key=TOKENS[0],
                  consumer_secret=TOKENS[1],
                  access_token_key=TOKENS[2],
                  access_token_secret=TOKENS[3])

meme_id = make_meme(context='twitter')
preview_meme(meme_id)

status = api.PostUpdate(
    "https://lambdabot.morchkovalski.com/meme_info/" + meme_id,
    media=open(os.path.join(DATA_DIR, 'previews', meme_id + '.jpg'), 'rb')
)
print("post added!")
print(status.id)
