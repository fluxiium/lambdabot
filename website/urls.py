from django.urls import path
from django.views.generic import RedirectView
from website import views
import lamdabotweb.settings as config

app_name = 'website'

urlpatterns = [
    path('', views.homepage, name='home_view'),
    path('meme/<uuid:meme_id>/', views.meme_info_view, name='meme_view'),
    path('meme_info/<uuid:meme_id>/', views.meme_info_view, name='meme_info_view'),
    path('generate/', views.meme_preview, name='meme_preview'),
    path('generate/<str:template>/', views.meme_preview, name='meme_preview_template'),
    path('oauth2_login/', views.oauth2.login, name='oauth2_login'),
    path('oauth2_logout/', views.oauth2.logout, name='oauth2_logout'),
    path('oauth2_callback/', views.oauth2.callback, name='oauth2_callback'),
    path('invite/', RedirectView.as_view(url=config.BOT_INVITE_URL, permanent=True), name='bot_invite'),
    path('discord/', RedirectView.as_view(url=config.DISCORD_SERVER_URL, permanent=True), name='discord_server'),
    path('submit/', views.submit, name='submit'),
    path('submit/<slug:channel_id>/', views.submit, name='submit_to_channel'),
]
