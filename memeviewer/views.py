import config
from django.http import Http404
from django.shortcuts import render
from memeviewer.models import Meem


def home_view(request):
    context = {
        'bot_name': config.BOT_NAME,
        'bot_name_twitter': config.TWITTER_USERNAME,
        'bot_name_facebook': config.FACEBOOK_USERNAME,
        'website_url': config.WEBSITE_URL,
    }

    return render(request, 'memeviewer/home.html', context)


def meme_info_view(request, meme_id):
    """ displays meme info page """

    try:
        meme = Meem.objects.get(meme_id=meme_id)
        meme.make_img()
    except Meem.DoesNotExist:
        raise Http404("Invalid meme ID")

    fb_meme = meme.facebookmeem_set.first()
    twitter_meme = meme.twittermeem_set.first()

    context = {
        'bot_name': config.BOT_NAME,
        'bot_name_twitter': config.TWITTER_USERNAME,
        'bot_name_facebook': config.FACEBOOK_USERNAME,
        'meme': meme,
        'facebook_url': fb_meme and fb_meme.post,
        'twitter_url': twitter_meme and twitter_meme.post,
        'website_url': config.WEBSITE_URL,
    }

    return render(request, 'memeviewer/meme_info_view.html', context)
