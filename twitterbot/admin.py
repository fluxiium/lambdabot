from django.contrib import admin
from twitterbot.models import TwitterPage
from memeviewer.models import Meem
from util.admin_utils import list_url


@admin.register(TwitterPage)
class TwitterPageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'enabled')
    fields = ('name', 'handle', 'consumer_key', 'consumer_secret', 'token_key', 'token_secret', 'image_pools', 'enabled', 'memes_link')
    readonly_fields = ('memes_link',)
    ordering = ('name',)

    def memes_link(self, obj: TwitterPage):
        return list_url(Meem, {'twittermeem__page': obj.pk}, 'Go')
    memes_link.short_description = 'Memes posted to this page'
