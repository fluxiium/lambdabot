from django.contrib import admin
from django.utils.safestring import mark_safe
from discordbot.models import DiscordServer, DiscordUser, DiscordChannel
from memeviewer.models import MemeSourceImage, Meem
from util.admin_utils import list_url


class DiscordChannelInline(admin.TabularInline):
    model = DiscordChannel
    extra = 0
    fields = ('name', 'channel_id', 'image_pools', 'submission_pool', 'disabled_cmds', 'blacklisted', 'links',)
    readonly_fields = ('name', 'channel_id', 'links')
    ordering = ('name',)
    can_delete = False

    def has_add_permission(self, request):
        return False

    def links(self, obj: DiscordChannel):
        return mark_safe(
            list_url(MemeSourceImage, {
                'discordsourceimgsubmission__discord_channel': obj.channel_id,
            }, 'Submitted images') + '<br>' +
            list_url(Meem, {
                'discordmeem__discord_channel': obj.channel_id,
            }, 'Generated memes')
        )
    links.short_description = 'Links'


@admin.register(DiscordServer)
class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'server_id', 'blacklisted')
    ordering = ('name',)
    search_fields = ('server_id', 'name',)
    readonly_fields = ('server_id', 'name', 'links')
    fields = ('name', 'server_id', 'prefix', 'disabled_cmds', 'blacklisted', 'links',)
    inlines = [DiscordChannelInline]

    def has_add_permission(self, request):
        return False

    def links(self, obj: DiscordServer):
        return mark_safe(
            list_url(MemeSourceImage, {
                'discordsourceimgsubmission__discord_channel__server': obj.server_id,
            }, 'Submitted images') + '<br>' +
            list_url(Meem, {
                'discordmeem__discord_channel__server': obj.server_id,
            }, 'Generated memes')
        )
    links.short_description = 'Links'


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_id', 'blacklisted')
    search_fields = ('user_id', 'name')
    ordering = ('name',)
    readonly_fields = ('user_id', 'name', 'links')
    fields = ('user_id', 'name', 'blacklisted', 'links')

    def has_add_permission(self, request):
        return False

    def links(self, obj: DiscordUser):
        return mark_safe(
            list_url(MemeSourceImage, {
                'discordsourceimgsubmission__discord_user': obj.user_id,
            }, 'Submitted images') + '<br>' +
            list_url(Meem, {
                'discordmeem__discord_user': obj.user_id,
            }, 'Generated memes')
        )
    links.short_description = 'Links'

    def lookup_allowed(self, key, value):
        return True
