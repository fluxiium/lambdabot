from django.urls import path, include
from rest_framework import routers
from webapi import views

app_name = 'webapi'

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'memeimagepool', views.MemeImagePoolViewSet)
router.register(r'memesourceimg', views.MemeSourceImageViewSet)
router.register(r'memetemplate', views.MemeTemplateViewSet)
router.register(r'meem', views.MeemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
