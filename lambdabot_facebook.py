# this script generates one meme and posts it to a facebook page

import os
import django
import facebook

from lamdabotweb.settings import FACEBOOK_PAGE_TOKEN

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem, MemeContext
from memeviewer.preview import preview_meme
from facebookbot.models import FacebookMeem

api = facebook.GraphAPI(FACEBOOK_PAGE_TOKEN)
meme = Meem.generate(context=MemeContext.by_id_or_create('facebook', 'Facebook'))
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

facebook_meme = FacebookMeem.objects.create(meme=meme, post=post_status['post_id'])
