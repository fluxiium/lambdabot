import os
import django
import facebook

from lamdabotweb.settings import DATA_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem, FacebookMeem
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
    "template and source images: {0}".format(meme.get_info_url())
)
print("comment added!")
print(comment_status)

facebook_meme = FacebookMeem(meme=meme, post=post_status['post_id'])
facebook_meme.save()
