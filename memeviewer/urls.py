from django.conf.urls import url

from . import views

app_name = 'memeviewer'

urlpatterns = [
    url(r'^template_preview/(?P<template_name>.*)', views.template_preview_view, name='template_preview_view'),
    url(r'^(?i)meme/(?P<meme_id>[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12})$',
        views.meme_info_view, name='meme_view'),
    url(r'^(?i)meme_info/(?P<meme_id>[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12})$',
        views.meme_info_view, name='meme_info_view'),
]
