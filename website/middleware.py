from datetime import timedelta, datetime
from django.utils import timezone
from discordbot.models import DiscordUser
import lamdabotweb.settings as config
from util.discord_api import revoke_discord_api_token, refresh_discord_api_token


def discord_oauth2_middleware(get_response):
    def middleware(request):
        request.website_url = config.WEBSITE_URL
        oauth2_session = request.session.get('oauth2_session')
        discord_data = request.session.get('discord_data')

        if oauth2_session is not None and discord_data is not None:
            last_refresh = datetime.utcfromtimestamp(discord_data['last_refresh'])
            if last_refresh + timedelta(seconds=(oauth2_session['expires_in'])) < timezone.now().utcnow():
                revoke_discord_api_token(request)
            elif last_refresh + timedelta(seconds=(oauth2_session['expires_in']) / 2) < timezone.now().utcnow():
                refresh_discord_api_token(request)
            oauth2_session = request.session.get('oauth2_session')
            discord_data = request.session.get('discord_data')

        if oauth2_session is not None and discord_data is not None:
            if config.DEBUG:
                print(oauth2_session)
                print(discord_data)
            request.user_data = DiscordUser.objects.get_or_create(user_id=discord_data['user']['id'], defaults={
                'name': discord_data['user']['username'],
            })[0]
        response = get_response(request)
        return response
    return middleware
