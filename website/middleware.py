from website import settings


def website_middleware(get_response):
    def middleware(request):
        request.website_url = settings.WEBSITE_URL
        response = get_response(request)
        return response
    return middleware
