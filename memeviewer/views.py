from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse
from django.shortcuts import render
from memeviewer.models import Meem, MemeImagePool, MemeTemplate


def home_view(request):
    return render(request, 'memeviewer/home.html')


def meme_info_view(request, meme_id):
    """ displays meme info page """

    try:
        meme = Meem.objects.get(meme_id=meme_id)
        meme.make_img()
    except Meem.DoesNotExist:
        raise Http404("Invalid meme ID")

    return render(request, 'memeviewer/meme_info_view.html', {
        'meme': meme,
    })


@staff_member_required
def preview_view(request, template=None):
    pools = MemeImagePool.objects.filter(name__in=request.GET.get('pools', '').split())
    try:
        template = template is not None and MemeTemplate.objects.get(name=template) or None
    except MemeTemplate.DoesNotExist:
        raise Http404("template does not exist")
    meme = Meem.generate(pools, 'default', saveme=False, template=template)
    response = HttpResponse(content_type='image/jpeg')
    meme.make_img(saveme=False).save(response, "JPEG")
    return response
