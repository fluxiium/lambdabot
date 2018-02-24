from django.conf.urls import url

from . import views

app_name = 'memeviewer'

urlpatterns = [
    url(r'^generate$', views.generate_meme_view, name='generate_meme_view'),
    url(r'^template_preview/(?P<template_name>.*)', views.template_preview_view, name='template_preview_view'),
    url(r'^reset_context/(?P<context>.*)', views.context_reset_view, name='context_reset_view'),
    url(r'^(?i)meme/(?P<meme_id>[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12})$',
        views.meme_info_view, name='meme_view'),
    url(r'^(?i)meme_info/(?P<meme_id>[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12})$',
        views.meme_info_view, name='meme_info_view'),
    url(r'^(?i)hdtfyet$', views.hdtfyet_view, name='hdtfyet_view'),
]
