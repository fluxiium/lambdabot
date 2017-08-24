from django.contrib import admin

from memeviewer.models import Meem, FacebookMeem, TwitterMeem, DiscordMeem


class FacebookInline(admin.TabularInline):
    model = FacebookMeem
    extra = 0


class TwitterInline(admin.TabularInline):
    model = TwitterMeem
    extra = 0


class DiscordInline(admin.TabularInline):
    model = DiscordMeem
    extra = 0


class MeemAdmin(admin.ModelAdmin):
    list_display = ('number', 'meme_id', 'template', 'context', 'gen_date')
    ordering = ('-number',)
    list_display_links = ('meme_id',)
    inlines = [FacebookInline, TwitterInline, DiscordInline]
    search_fields = ('number', 'meme_id', 'context', 'template')

admin.site.register(Meem, MeemAdmin)
