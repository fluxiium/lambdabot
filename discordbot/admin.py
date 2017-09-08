from django.contrib import admin

from discordbot.models import DiscordServer, DiscordCommand, DiscordMeem


class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('server_id', 'context')
    ordering = ('context', 'server_id')
    search_fields = ('server_id', 'context__name', 'context__short_name')

admin.site.register(DiscordServer, DiscordServerAdmin)


class DiscordCommandAdmin(admin.ModelAdmin):
    list_display = ('cmd', 'help', 'message')
    ordering = ('cmd',)
    search_fields = ('cmd',)


admin.site.register(DiscordCommand, DiscordCommandAdmin)


class DiscordMeemAdmin(admin.ModelAdmin):
    list_display = ('meme', 'server')
    search_fields = ('meme__number', 'meme__meme_id', 'meme__context_link__name', 'meme__context_link__short_name',
                     'meme__template_link__name', 'meme__sourceimgs', 'server__server_id')

# admin.site.register(DiscordMeem, DiscordMeemAdmin)
