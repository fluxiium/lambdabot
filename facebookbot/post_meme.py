import os
import django
import facebook

from lamdabotweb.settings import DATA_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem
from memeviewer.preview import preview_meme

token_file = open(os.path.join(DATA_DIR, 'fbtoken.txt'), 'r')
PAGE_TOKEN = token_file.read()
token_file.close()

api = facebook.GraphAPI(PAGE_TOKEN)
meme = Meem.generate(context='facebook')
preview_meme(meme)

post_status = api.put_photo(open(meme.get_local_path(), 'rb'))
print("post added!")
print(post_status)

comment_status = api.put_comment(
    post_status['id'],
    "template and source images: https://lambdabot.morchkovalski.com/meme_info/" + meme.meme_id
)
print("comment added!")
print(comment_status)
