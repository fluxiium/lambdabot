from discordbot.models import DiscordUser
from website import settings


def website_middleware(get_response):
    def middleware(request):
        request.website_url = settings.WEBSITE_URL
        if request.user.is_authenticated:
            if hasattr(request, 'discord_user'):
                request.discord_user, _ = DiscordUser.objects.get_or_create(
                    user_id=request.discord_user.discord_id,
                    defaults={'name': request.discord_user.name})
            else:
                request.discord_user = None
        response = get_response(request)
        return response
    return middleware
