import os

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, redirect

from lamdabotweb.settings import STATIC_URL
from memeviewer.models import Meem, MemeContext, MemeTemplate, ImageInContext
from memeviewer.preview import preview_meme


def generate_meme_view(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    meme = Meem.generate(context=MemeContext.by_id('template_preview'))
    return redirect(meme.get_info_url())


def template_preview_view(request, template_name):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    try:
        meme = Meem.generate(
            context=MemeContext.by_id('template_preview'),
            template=MemeTemplate.find(template_name),
        )
    except ObjectDoesNotExist:
        raise Http404("template does not exist")

    return redirect(meme.get_info_url())


def context_reset_view(request, context):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    queue = ImageInContext.objects.filter(context_link=MemeContext.by_id(context))
    templates = []
    sourceimgs = []

    for item in queue:
        if item.image_type == ImageInContext.IMAGE_TYPE_TEMPLATE:
            templates.append(item.image_name)
        else:
            sourceimgs.append(item.image_name)
        item.delete()

    return JsonResponse({
        'templates': templates,
        'sourceimgs': sourceimgs,
    })


def meme_info_view(request, meme_id):
    try:
        meme = Meem.objects.get(meme_id=meme_id)
        if not os.path.isfile(meme.get_local_path()):
            preview_meme(meme)
    except ObjectDoesNotExist:
        raise Http404("Invalid meme ID")

    templatebg = None
    if meme.template_link.bg_img != '':
        templatebg = STATIC_URL + 'lambdabot/resources/templates/' + meme.template_link.bg_img

    fb_meme = meme.facebookmeem_set.first()
    twitter_meme = meme.twittermeem_set.first()

    context = {
        'meme_id': meme_id,
        'meme_url': meme.get_url(),
        'meme_info_url': meme.get_info_url(),
        'template_name': meme.template_link.name,
        'template_url': meme.template_link.get_image_url(),
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
