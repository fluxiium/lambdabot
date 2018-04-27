from django.urls import path

from . import views

app_name = 'memeviewer'

urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('generate', views.generate_meme_view, name='generate_meme_view'),
    path('template_preview/<template_name>', views.template_preview_view, name='template_preview_view'),
    path('meme/<uuid:meme_id>', views.meme_info_view, name='meme_view'),
    path('meme_info/<uuid:meme_id>', views.meme_info_view, name='meme_info_view'),
]
