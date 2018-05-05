import json
from django.utils import timezone
from requests import HTTPError
import lamdabotweb.settings as config
import requests
from django.shortcuts import redirect


def discord_api(request, api_path):
    oauth2_session = request.session.get('oauth2_session')
    if oauth2_session is None:
        return revoke_discord_api_token(request)
    now = timezone.now().timestamp()
    request.session['discord_api'] = request.session.get('discord_api', {})
    current = request.session['discord_api'].get(api_path)
    refresh_after = 0 if current is None else current['refresh_after']
    if refresh_after < now:
        auth = 'Bearer ' + oauth2_session['access_token']
        r = requests.get(config.DISCORD_API_ROOT + api_path, headers={'Authorization': auth})
        try:
            r.raise_for_status()
        except HTTPError:
            return revoke_discord_api_token(request)
        result = json.loads(r.text)
        try:
            result['refresh_after'] = now + 10
        except TypeError:
            result = {
                'list': result,
                'refresh_after': now + 10,
            }
        request.session['discord_api'][api_path] = result
        return result
    return current


def refresh_discord_api_token(request, code=None):
    oauth2_session = request.session.get('oauth2_session')
    now = timezone.now().timestamp()
    if code:
        data = {
            'grant_type': 'authorization_code',
            'code': code,
        }
    elif oauth2_session:
        refresh_after = oauth2_session['refresh_after']
        expires = oauth2_session['expires']
        if expires < now:
            return revoke_discord_api_token(request)
        elif refresh_after > now:
            return oauth2_session
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': oauth2_session['refresh_token'],
        }
    else:
        return None
    data.update({
        'client_id': config.OAUTH2_CLIENT_ID,
        'client_secret': config.OAUTH2_CLIENT_SECRET,
        'redirect_uri': config.OAUTH2_REDIRECT_URI,
    })
    r = requests.post(config.OAUTH2_TOKEN_URL, data, {'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        r.raise_for_status()
    except HTTPError:
        return revoke_discord_api_token(request)
    oauth2_session = json.loads(r.text)
    oauth2_session['refresh_after'] = now + (oauth2_session['expires_in'] / 2)
    oauth2_session['expires'] = now + oauth2_session['expires_in']
    request.session['oauth2_session'] = oauth2_session


def revoke_discord_api_token(request):
    oauth2_session = request.session.get('oauth2_session')
    discord_data = request.session.get('discord_api')
    if oauth2_session is not None:
        requests.get(config.OAUTH2_REVOKE_URL, {'token': oauth2_session['access_token']})
        del request.session['oauth2_session']
    if discord_data is not None:
        del request.session['discord_api']
    return None


def discord_login_required(f):
    def wrapper(request, *args, **kw):
        if request.user_data is None:
            request.session['oauth2_next'] = 'website:submit'
            return redirect('website:oauth2_login')
        else:
            return f(request, *args, **kw)
    return wrapper
