import os
import config

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render
from memeviewer.models import Meem, MemeContext, MemeTemplate, MemeSourceImageInContext, MemeTemplateInContext
from memeviewer.preview import preview_meme


def home_view(request):
    context = {
        'bot_name': config.BOT_NAME,
        'bot_name_twitter': config.USERNAME_TWITTER,
        'bot_name_facebook': config.USERNAME_FACEBOOK,
        'website_url': config.WEBSITE_URL,
    }

    return render(request, 'memeviewer/home.html', context)


def generate_meme_view(request):
    """ generates and displays random meme """

    if not request.user.has_perm('memetemplate.change_memetemplate'):
        return HttpResponseForbidden()

    meme = MemeContext.by_id_or_create('default', 'Default').generate(saveme=False)

    response = HttpResponse(content_type='image/jpeg')
    preview_meme(meme, saveme=False).save(response, "JPEG")
    return response


def template_preview_view(request, template_name):
    """ generates and displays random meme with given template """

    if not request.user.has_perm('memetemplate.change_memetemplate'):
        return HttpResponseForbidden()

    try:
        meme = MemeContext.by_id_or_create('default', 'Default').generate(
            template=MemeTemplate.find(template_name, allow_disabled=True),
            saveme=False
        )
    except ObjectDoesNotExist:
        raise Http404("template does not exist")

    response = HttpResponse(content_type='image/jpeg')
    preview_meme(meme, saveme=False).save(response, "JPEG")
    return response


def context_reset_view(request, context):
    """ clears image queue of given context, displays lists of images that were in the queue """

    if not request.user.has_perm('memecontext.change_memecontext'):
        return HttpResponseForbidden()

    siq = MemeSourceImageInContext.objects.filter(queued=True)
    if context:
        siq = siq.filter(context=MemeContext.by_id(context))

    tq = MemeTemplateInContext.objects.filter(queued=True)
    if context:
        tq = siq.filter(context=MemeContext.by_id(context))

    for i in list(siq) + list(tq):
        i.queued = False
        i.save()

    return HttpResponse('ok')


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
        'bot_name': config.BOT_NAME,
        'bot_name_twitter': config.USERNAME_TWITTER,
        'bot_name_facebook': config.USERNAME_FACEBOOK,
        'meme': meme,
        'facebook_url': fb_meme and fb_meme.post,
        'twitter_url': twitter_meme and twitter_meme.post,
        'website_url': config.WEBSITE_URL,
    }

    return render(request, 'memeviewer/meme_info_view.html', context)
