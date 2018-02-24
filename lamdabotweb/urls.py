from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

from lamdabotweb import settings
from lamdabotweb.settings import BOT_NAME

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('memeviewer.urls')),
    url(r'^$', RedirectView.as_view(url="https://fb.com/lambdabot")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = BOT_NAME + ' administration'
