import facebook
from django.core.management import BaseCommand
from facebookbot.models import FacebookMeem, FacebookPage


class Command(BaseCommand):
    help = 'Posts a meme to facebook'

    def handle(self, *args, **options):
        for p in FacebookPage.objects.all():
            api = facebook.GraphAPI(p.token)

            meme = p.generate_meme()
            meme.make_img()

            post_status = api.put_photo(open(meme.get_local_path(), 'rb'))
            print("post added!")
            print(post_status)

            comment_status = api.put_comment(
                post_status['id'],
                "template and source images: {0}".format(meme.get_info_url())
            )
            print("comment added!")
            print(comment_status)

            FacebookMeem.objects.filter(meme=meme).update(post=post_status['post_id'])
