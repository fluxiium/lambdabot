from django.urls import path
from website import views

app_name = 'website'

urlpatterns = [
    path('', views.homepage, name='home_view'),
    path('meme/<uuid:meme_id>', views.meme_info_view, name='meme_view'),
    path('meme_info/<uuid:meme_id>', views.meme_info_view, name='meme_info_view'),
    path('generate', views.meme_preview, name='meme_preview'),
    path('generate/<str:template>', views.meme_preview, name='meme_preview_template'),
    path('oauth2_login', views.oauth2.login, name='oauth2_login'),
    path('oauth2_logout', views.oauth2.logout, name='oauth2_logout'),
    path('oauth2_callback', views.oauth2.callback, name='oauth2_callback'),
]
