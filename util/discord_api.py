import json
from django.utils import timezone
import lamdabotweb.settings as config
import requests


def discord_api(path, token=None):
    if not token:
        auth = 'Bot ' + config.DISCORD_TOKEN
    else:
        auth = 'Bearer ' + token
    r = requests.get(config.DISCORD_API_ROOT + path, headers={'Authorization': auth})
    r.raise_for_status()
    return json.loads(r.text)


def refresh_discord_api_token(request, code=None):
    oauth2_session = request.session.get('oauth2_session')
    if code:
        data = {
            'grant_type': 'authorization_code',
            'code': code,
        }
    elif oauth2_session:
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': oauth2_session['refresh_token'],
        }
    else:
        return
    data.update({
        'client_id': config.OAUTH2_CLIENT_ID,
        'client_secret': config.OAUTH2_CLIENT_SECRET,
        'redirect_uri': config.OAUTH2_REDIRECT_URI,
    })
    r = requests.post(config.OAUTH2_TOKEN_URL, data, {'Content-Type': 'application/x-www-form-urlencoded'})
    r.raise_for_status()
    oauth2_session = json.loads(r.text)
    request.session['oauth2_session'] = oauth2_session
    request.session['discord_data'] = {
        'last_refresh': timezone.now().timestamp(),
        'user': discord_api('/users/@me', oauth2_session['access_token']),
    }


def revoke_discord_api_token(request):
    oauth2_session = request.session.get('oauth2_session')
    discord_data = request.session.get('discord_data')
    if oauth2_session is not None and discord_data is not None:
        requests.get(config.OAUTH2_REVOKE_URL, {'token': oauth2_session['access_token']})
        del request.session['oauth2_session']
        del request.session['discord_data']
