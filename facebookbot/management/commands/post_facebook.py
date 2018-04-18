import facebook
from django.core.management import BaseCommand
from config import FACEBOOK_PAGE_TOKEN
from memeviewer.models import MemeContext
from memeviewer.preview import preview_meme
from facebookbot.models import FacebookMeem


class Command(BaseCommand):
    help = 'Posts a meme to facebook'

    def handle(self, *args, **options):
        api = facebook.GraphAPI(FACEBOOK_PAGE_TOKEN)
        meme = MemeContext.by_id_or_create('facebook', 'Facebook', is_public=True).generate()
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

        FacebookMeem.objects.create(meme=meme, post=post_status['post_id'])
