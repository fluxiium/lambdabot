from rest_framework import viewsets
from memeviewer import models
from webapi import serializers

class MemeImagePoolViewSet(viewsets.ModelViewSet):
    queryset = models.MemeImagePool.objects.order_by('name')
    serializer_class = serializers.MemeImagePoolSerializer
    lookup_field = 'name'

class MemeSourceImageViewSet(viewsets.ModelViewSet):
    queryset = models.MemeSourceImage.objects.order_by('add_date')
    serializer_class = serializers.MemeSourceImageSerializer
    lookup_value_regex = '[^/]+'
    lookup_field = 'name'

class MemeTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.MemeTemplate.objects.order_by('add_date')
    serializer_class = serializers.MemeTemplateSerializer
    lookup_value_regex = '.+'
    lookup_field = 'name'

class MeemViewSet(viewsets.ModelViewSet):
    queryset = models.Meem.objects.order_by('number')
    serializer_class = serializers.MeemSerializer
    lookup_field = 'meme_id'
