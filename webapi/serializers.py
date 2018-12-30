from rest_framework import serializers
from memeviewer import models

class MemeImagePoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.MemeImagePool
        fields = ('name', 'friendly_name', 'pool_type',)

class MemeSourceImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.MemeSourceImage
        fields = ('name', 'friendly_name', 'image_pool', 'accepted', 'add_date', 'image_url',)
    image_pool = serializers.HyperlinkedRelatedField(view_name='webapi:memeimagepool-detail', lookup_field='name', queryset=models.MemeImagePool.objects.order_by('name'))

class MemeTemplateSlotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.MemeTemplateSlot
        fields = ('slot_order', 'x', 'y', 'w', 'h', 'rotate', 'blur', 'grayscale', 'cover')

class MemeTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.MemeTemplate
        fields = ('name', 'friendly_name', 'image_pool', 'accepted', 'add_date', 'bg_image_file', 'image_file', 'bg_color', 'slots', 'image_url', 'bgimage_url',)
    image_pool = serializers.HyperlinkedRelatedField(view_name='webapi:memeimagepool-detail', lookup_field='name', queryset=models.MemeImagePool.objects.order_by('name'))
    slots = MemeTemplateSlotSerializer(source='memetemplateslot_set', many=True)

class MeemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Meem
        fields = ('number', 'meme_id', 'template_link', 'gen_date', 'source_images', 'url', 'info_url')
    template_link = serializers.HyperlinkedRelatedField(view_name='webapi:memetemplate-detail', lookup_field='name', queryset=models.MemeTemplate.objects.order_by('name'))
