from django.urls import path, include
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from webapi import views

app_name = 'webapi'

schema_view = get_schema_view(title='LambdaBot API')

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'memeimagepool', views.MemeImagePoolViewSet)
router.register(r'memesourceimg', views.MemeSourceImageViewSet)
router.register(r'memetemplate', views.MemeTemplateViewSet)
router.register(r'meem', views.MeemViewSet)

urlpatterns = [
    path('schema/', schema_view),
    path('', include(router.urls)),
]
