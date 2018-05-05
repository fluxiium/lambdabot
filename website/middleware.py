from discordbot.models import DiscordUser
import lamdabotweb.settings as config
from website.discord_api import refresh_discord_api_token, discord_api


def discord_oauth2_middleware(get_response):
    def middleware(request):
        request.website_url = config.WEBSITE_URL

        oauth2_session = refresh_discord_api_token(request)
        discord_user_data = discord_api(request, '/users/@me')

        if config.DEBUG:
            print(oauth2_session)
            print(discord_user_data)

        if discord_user_data is not None:
            request.user_data = DiscordUser.objects.get_or_create(user_id=discord_user_data['id'], defaults={
                'name': discord_user_data['username'],
            })[0]
        else:
            request.user_data = None
        response = get_response(request)
        return response
    return middleware
