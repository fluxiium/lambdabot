import lamdabotweb.settings as config
from django.http import HttpResponse
from django.shortcuts import redirect
from util.discord_api import revoke_discord_api_token, refresh_discord_api_token
from util import struuid4


def login(request):
    state = struuid4()
    scope = 'identify'
    request.session['oauth2_state'] = state
    return redirect('https://discordapp.com/api/oauth2/authorize?client_id={0}&redirect_uri={1}&response_type=code&scope={2}&state={3}'.format(
        config.OAUTH2_CLIENT_ID, config.OAUTH2_REDIRECT_URI, scope, state
    ))


def logout(request):
    revoke_discord_api_token(request)
    return redirect('website:home_view')


def callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    if not code or not state or state != request.session.get('oauth2_state'):
        return HttpResponse('401 Unauthorized', status=401)
    refresh_discord_api_token(request, code=code)
    return redirect('website:home_view')
