from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render

from lambdabot.preview import preview_meme
from lambdabot.settings import *
from lambdabot.db import get_resource_path, meme_info_page


def meme_view(request, meme_id):

    try:
        meme_img = preview_meme(meme_id=meme_id)
    except KeyError:
        raise Http404("Invalid meme ID")

    response = HttpResponse(content_type='image/png')
    meme_img.save(response, 'PNG')
    return response


def resource_view(request, resource_id):
    resource_path, content_type = get_resource_path(resource_id)
    print("shit")

    if resource_path is None:
        raise Http404("Invalid resource ID")

    resource = open(os.path.join(RESOURCE_DIR, resource_path), 'rb').read()
    return HttpResponse(resource, content_type=content_type)


def meme_info_view(request, meme_id):
    try:
        template_url, template_bg_url, source_urls, context, gen_date, num = meme_info_page(meme_id=meme_id)
    except KeyError:
        raise Http404("Invalid meme ID")

    context = {
        'meme_id': meme_id,
        'template_url': template_url,
        'template_bg_url': template_bg_url,
        'source_urls': source_urls,
        'context': CONTEXTS[context],
        'gen_date': gen_date,
        'num': num,
    }
    return render(request, 'memeviewer/meme_info_view.html', context)
