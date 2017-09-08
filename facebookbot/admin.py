from django.contrib import admin

from facebookbot.models import FacebookMeem


class FacebookMeemAdmin(admin.ModelAdmin):
    list_display = ('meme', 'post')
    search_fields = ('meme__number', 'meme__meme_id', 'meme__context_link__name', 'meme__context_link__short_name',
                     'meme__template_link__name', 'meme__sourceimgs', 'post')

# admin.site.register(FacebookMeem, FacebookMeemAdmin)
