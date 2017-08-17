import facebook

from lambdabot.preview import preview_meme
from lambdabot.db import make_meme
from lambdabot.settings import *

token_file = open(os.path.join(DATA_DIR, 'fbtoken.txt'), 'r')
PAGE_TOKEN = token_file.read()
token_file.close()

api = facebook.GraphAPI(PAGE_TOKEN)
meme_id = make_meme(context='facebook')
preview_meme(meme_id)

post_status = api.put_photo(open(os.path.join(DATA_DIR, 'previews', meme_id + '.jpg'), 'rb'))
print("post added!")
print(post_status)

comment_status = api.put_comment(
    post_status['id'],
    "template and source images: https://lambdabot.morchkovalski.com/meme_info/" + meme_id
)
print("comment added!")
print(comment_status)
