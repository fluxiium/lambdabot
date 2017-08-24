from django.http import Http404
from django.shortcuts import render

from lamdabotweb.settings import CONTEXTS, MEME_TEMPLATES, STATIC_URL
from memeviewer.models import Meem


def meme_info_view(request, meme_id):
    meme = Meem.objects.get(meme_id=meme_id)
    if meme is None:
        raise Http404("Invalid meme ID")

    templatebg = MEME_TEMPLATES[meme.template].get('bgimg')
    if templatebg is not None:
        templatebg = STATIC_URL + 'lambdabot/resources/templates/' + templatebg

    context = {
        'meme_id': meme_id,
        'meme_url': meme.get_url(),
        'template_url': STATIC_URL + 'lambdabot/resources/templates/' + meme.template,
        'template_bg_url': templatebg,
        'source_urls':
            [STATIC_URL + 'lambdabot/resources/sourceimg/' + sourceimg for sourceimg in meme.get_sourceimgs()],
        'context': CONTEXTS.get(meme.context, meme.context),
        'gen_date': meme.gen_date,
        'num': meme.number,
    }
    return render(request, 'memeviewer/meme_info_view.html', context)
