from captcha.fields import ReCaptchaField
from django import forms
from django.core.exceptions import ValidationError
from discordbot.models import DiscordUser, DiscordChannel
from memeviewer.models import MemeSourceImage, POOL_TYPE_SRCIMGS, POOL_TYPE_ALL, MemeImagePool
from website import settings


class MemeSourceImageForm(forms.ModelForm):
    class Meta:
        model = MemeSourceImage
        fields = ('friendly_name', 'image_pool', 'image_file', 'captcha')
        widgets = {
            'friendly_name': forms.TextInput(attrs={'placeholder': 'Image name'}),
        }

    def __init__(self, user: DiscordUser, channel: DiscordChannel = None, *args, **kwargs):
        super(MemeSourceImageForm, self).__init__(*args, **kwargs)
        avail = user.available_pools(channel).filter(pool_type__in=[POOL_TYPE_SRCIMGS, POOL_TYPE_ALL])
        self.fields['image_pool'] = forms.ModelChoiceField(avail.order_by('friendly_name'), empty_label=None)
        try:
            self.initial['image_pool'] = channel and channel.submission_pool or avail.get(name='halflife')
        except MemeImagePool.DoesNotExist:
            pass

    def clean_image_file(self):
        image = self.cleaned_data['image_file']
        if image.size > settings.MEEM_MAX_SRCIMG_SIZE:
            raise ValidationError('Image is too big (should be smaller than %(size)s KB)', params={'size': settings.MEEM_MAX_SRCIMG_SIZE / 1000})
        return image

    captcha = ReCaptchaField()
