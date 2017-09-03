import os

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from lamdabotweb.settings import STATIC_URL
from memeviewer.models import Meem, MemeContext, MemeTemplate
from memeviewer.preview import preview_meme


def template_preview_view(request, template_name):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    try:
        meme = Meem.generate(
            context=MemeContext.by_id('template_preview'),
            template=MemeTemplate.objects.get(name=template_name),
        )
    except ObjectDoesNotExist:
        raise Http404("template does not exist")

    return redirect(meme.get_info_url())


def meme_info_view(request, meme_id):
    try:
        meme = Meem.objects.get(meme_id=meme_id)
        if not os.path.isfile(meme.get_local_path()):
            preview_meme(meme)
    except ObjectDoesNotExist:
        raise Http404("Invalid meme ID")

    templatebg = None
    if meme.template_link.bg_img is not None:
        templatebg = STATIC_URL + 'lambdabot/resources/templates/' + meme.template_link.bg_img

    fb_meme = meme.facebookmeem_set.first()
    twitter_meme = meme.twittermeem_set.first()

    context = {
        'meme_id': meme_id,
        'meme_url': meme.get_url(),
        'meme_info_url': meme.get_info_url(),
        'template_url': STATIC_URL + 'lambdabot/resources/templates/' + meme.template_link.name,
        'template_bg_url': templatebg,
        'source_urls':
            [STATIC_URL + 'lambdabot/resources/sourceimg/' + sourceimg for sourceimg in meme.get_sourceimgs()],
        'context': meme.context_link.name,
        'gen_date': meme.gen_date,
        'num': meme.number,
        'facebook_url': fb_meme and 'https://facebook.com/{0}'.format(fb_meme.post),
        'twitter_url': twitter_meme and 'https://twitter.com/lambdabot3883/status/{0}'.format(twitter_meme.post),
    }

    return render(request, 'memeviewer/meme_info_view.html', context)
