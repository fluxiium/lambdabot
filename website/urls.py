from django.urls import path
from django.views.generic import RedirectView
from website import views, settings

app_name = 'website'

urlpatterns = [
    path('', views.homepage, name='home_view'),
    path('meme/<uuid:meme_id>/', views.meme_info_view, name='meme_view'),
    path('meme_info/<uuid:meme_id>/', views.meme_info_view, name='meme_info_view'),
    path('generate/', views.meme_preview, name='meme_preview'),
    path('generate/<str:template>/', views.meme_preview, name='meme_preview_template'),
    path('invite/', RedirectView.as_view(url=settings.BOT_INVITE_URL, permanent=True), name='bot_invite'),
    path('submit/', views.submit, name='submit'),
]
