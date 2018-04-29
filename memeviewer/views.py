from django.http import Http404
from django.shortcuts import render
from memeviewer.models import Meem


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
