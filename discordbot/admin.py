from django.contrib import admin
from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser, DiscordUser
from memeviewer.models import MemeSourceImage, Meem
from util.admin_utils import list_url, object_url


class DiscordCommandInline(admin.TabularInline):
    model = DiscordCommand
    extra = 0


class DiscordServerUserInline(admin.TabularInline):
    model = DiscordServerUser
    extra = 0
    verbose_name_plural = "Server-specific"
    fields = ('server_link', 'submissions_link', 'memes_link', 'blacklisted')
    readonly_fields = ('server_link', 'submissions_link', 'memes_link')
    ordering = ('server__name',)
    can_delete = False

    def has_add_permission(self, request):
        return False

    def server_link(self, obj):
        return object_url(DiscordServer, obj.server_id, obj.server)
    server_link.short_description = 'Server'

    def submissions_link(self, obj):
        return list_url(MemeSourceImage, {
            'discordsourceimgsubmission__discord_user__user_id': obj.user_id,
            'discordsourceimgsubmission__discord_server__server_id': obj.server_id,
        }, obj.submission_count)
    submissions_link.short_description = 'Submitted images'

    def memes_link(self, obj):
        return list_url(Meem, {
            'discordmeem__discord_user__user_id': obj.user_id,
            'discordmeem__discord_server__server_id': obj.server_id,
        }, obj.meme_count)
    memes_link.short_description = 'Generated memes'


@admin.register(DiscordServer)
class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'context', 'user_count', 'submission_count', 'meme_count', 'blacklisted')
    ordering = ('name',)
    search_fields = ('server_id', 'name', 'context__short_name')
    readonly_fields = ('server_id', 'name', 'users_link', 'submissions_link', 'memes_link')
    fields = readonly_fields + ('context', 'prefix', 'blacklisted')
    inlines = [DiscordCommandInline]

    def has_add_permission(self, request):
        return False

    def users_link(self, obj):
        return list_url(DiscordUser, {
            'discordserveruser__server__server_id': obj.server_id,
        }, obj.user_count)
    users_link.short_description = 'Users'

    def submissions_link(self, obj):
        return list_url(MemeSourceImage, {
            'discordsourceimgsubmission__discord_server__server_id': obj.server_id,
        }, obj.submission_count)
    submissions_link.short_description = 'Submitted images'

    def memes_link(self, obj):
        return list_url(Meem, {
            'discordmeem__discord_server__server_id': obj.server_id,
        }, obj.meme_count)
    memes_link.short_description = 'Generated memes'


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_id', 'server_count', 'submission_count', 'meme_count', 'blacklisted')
    search_fields = ('user_id', 'name')
    ordering = ('name',)
    readonly_fields = ('user_id', 'name', 'submissions_link', 'memes_link')
    fields = readonly_fields + ('blacklisted',)
    inlines = [DiscordServerUserInline]

    def has_add_permission(self, request):
        return False

    def submissions_link(self, obj):
        return list_url(MemeSourceImage, {
            'discordsourceimgsubmission__discord_user__user_id': obj.user_id,
        }, obj.submission_count)
    submissions_link.short_description = 'Submitted images'

    def memes_link(self, obj):
        return list_url(Meem, {
            'discordmeem__discord_user__user_id': obj.user_id,
        }, obj.meme_count)
    memes_link.short_description = 'Generated memes'

    def lookup_allowed(self, key, value):
        if key in (
            'discordserveruser__server__server_id',
        ):
            return True
        return super(DiscordUserAdmin, self).lookup_allowed(key, value)
