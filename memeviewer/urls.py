from django.urls import path

from . import views

app_name = 'memeviewer'

urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('meme/<uuid:meme_id>', views.meme_info_view, name='meme_view'),
    path('meme_info/<uuid:meme_id>', views.meme_info_view, name='meme_info_view'),
    path('generate', views.preview_view, name='preview_view'),
    path('generate/<str:template>', views.preview_view, name='template_preview_view'),
]
