from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from lamdabotweb.settings import BOT_NAME, ROOT_REDIRECT

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('memeviewer.urls')),
    url(r'^$', RedirectView.as_view(url=ROOT_REDIRECT)),
]

admin.site.site_header = BOT_NAME + ' administration'
