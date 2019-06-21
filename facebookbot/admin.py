from django.contrib import admin
from facebookbot.models import FacebookPage
from memeviewer.models import Meem
from util.admin_utils import list_url


@admin.register(FacebookPage)
class FacebookPageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'page_id', 'enabled')
    fields = ('page_id', 'name', 'token', 'image_pools', 'enabled', 'memes_link')
    readonly_fields = ('memes_link',)
    ordering = ('name',)

    def memes_link(self, obj: FacebookPage):
        return list_url(Meem, {'facebookmeem__page': obj.page_id}, 'Go')
    memes_link.short_description = 'Memes posted to this page'
