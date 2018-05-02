import website.views.oauth2
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse
from memeviewer.models import Meem, MemeImagePool, MemeTemplate
from django.shortcuts import render

def homepage(request):

    # return HttpResponse(oauth.get('https://discordapp.com/api/users/@me'))
    return render(request, 'website/home.html')


def meme_info_view(request, meme_id):
    """ displays meme info page """

    try:
        meme = Meem.objects.get(meme_id=meme_id)
        meme.make_img()
    except Meem.DoesNotExist:
        raise Http404("Invalid meme ID")

    return render(request, 'website/meme_info_view.html', {
        'meme': meme,
    })


@staff_member_required
def meme_preview(request, template=None):
    pools = MemeImagePool.objects.filter(name__in=request.GET.get('pools', '').split())
    try:
        template = template is not None and MemeTemplate.objects.get(name=template) or None
    except MemeTemplate.DoesNotExist:
        raise Http404("template does not exist")
    meme = Meem.generate(pools, 'default', saveme=False, template=template)
    response = HttpResponse(content_type='image/jpeg')
    meme.make_img(saveme=False).save(response, "JPEG")
    return response
