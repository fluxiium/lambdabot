from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse
from discordbot.models import DiscordMeem, DiscordServer, DiscordChannel, DiscordSourceImgSubmission
from memeviewer.models import Meem, MemeImagePool, MemeTemplate, MemeSourceImage
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from website.forms import MemeSourceImageForm


def homepage(request):
    return render(request, 'website/home.html', {
        'discord_meme_count': DiscordMeem.objects.count(),
        'sourceimg_count': MemeSourceImage.objects.filter(accepted=True).count(),
        'template_count': MemeTemplate.objects.filter(accepted=True).count(),
        'users_count': DiscordMeem.objects.values_list('discord_user__user_id', flat=True).distinct().count(),
        'servers_count': DiscordServer.objects.count(),
        'meme_count': Meem.objects.order_by('-gen_date').first().number,
    })


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


@login_required
def submit(request, channel_id=None):
    channel = None
    # todo: what if not logged in through discord?
    if channel_id:
        try:
            channel = request.discord_user.discordchannel_set.get(channel_id=channel_id)
        except DiscordChannel.DoesNotExist:
            return redirect('website:submit')  # todo: error msg
    if request.method == 'POST':
        form = MemeSourceImageForm(request.discord_user, channel, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            DiscordSourceImgSubmission.objects.create(sourceimg=form.instance, discord_user=request.discord_user, discord_channel=channel)
            return render(request, 'website/submit.html', {'success': True})  # todo: dank u msg
        else:
            print(form.errors)
            return render(request, 'website/submit.html', {'form': form, 'success': False})  # todo: errors
    else:
        form = MemeSourceImageForm(request.discord_user, channel)
    return render(request, 'website/submit.html', {'form': form})
