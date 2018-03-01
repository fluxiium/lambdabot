import os

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, redirect

from lamdabotweb.settings import USERNAME_FACEBOOK, USERNAME_TWITTER, BOT_NAME
from memeviewer.models import Meem, MemeContext, MemeTemplate, ImageInContext
from memeviewer.preview import preview_meme


def generate_meme_view(request):
    """ generates and displays random meme """

    if not request.user.has_perm('memetemplate.change_memetemplate'):
        return HttpResponseForbidden()

    meme = Meem.generate(context=MemeContext.by_id_or_create('default', 'Default'))
    return redirect(meme.get_info_url())


def template_preview_view(request, template_name):
    """ generates and displays random meme with given template """

    if not request.user.has_perm('memetemplate.change_memetemplate'):
        return HttpResponseForbidden()

    try:
        meme = Meem.generate(
            context=MemeContext.by_id_or_create('default', 'Default'),
            template=MemeTemplate.find(template_name, allow_disabled=True),
        )
    except ObjectDoesNotExist:
        raise Http404("template does not exist")

    return redirect(meme.get_info_url())


def context_reset_view(request, context):
    """ clears image queue of given context, displays lists of images that were in the queue """

    if not request.user.has_perm('memecontext.change_memecontext'):
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
    """ displays meme info page """

    try:
        meme = Meem.objects.get(meme_id=meme_id)
        if not os.path.isfile(meme.get_local_path()):
            preview_meme(meme)
    except ObjectDoesNotExist:
        raise Http404("Invalid meme ID")

    fb_meme = meme.facebookmeem_set.first()
    twitter_meme = meme.twittermeem_set.first()

    context = {
        'bot_name': BOT_NAME,
        'bot_name_twitter': USERNAME_TWITTER,
        'bot_name_facebook': USERNAME_FACEBOOK,
        'meme': meme,
        'facebook_url': fb_meme and fb_meme.post,
        'twitter_url': twitter_meme and twitter_meme.post,
    }

    return render(request, 'memeviewer/meme_info_view.html', context)
