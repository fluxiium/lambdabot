from django.conf.urls import url

from . import views

app_name = 'memeviewer'

urlpatterns = [
    url(r'^(?i)meme/(?P<meme_id>[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12})$',
        views.meme_view, name='meme_view'),
    url(r'^(?i)resource/(?P<resource_id>[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12})$',
        views.resource_view, name='resource_view'),
    url(r'^(?i)meme_info/(?P<meme_id>[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12})$',
        views.meme_info_view, name='meme_info_view'),
]
