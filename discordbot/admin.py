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
    fields = ('server_link', 'unlimited_memes', 'submissions_link', 'memes_link')
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
            'discordsourceimgsubmission__server_user__user__user_id': obj.user_id,
            'discordsourceimgsubmission__server_user__server__server_id': obj.server_id,
        }, obj.submission_count)
    submissions_link.short_description = 'Submitted images'

    def memes_link(self, obj):
        return list_url(Meem, {
            'discordmeem__server_user__user__user_id': obj.user_id,
            'discordmeem__server_user__server__server_id': obj.server_id,
        }, obj.meme_count)
    memes_link.short_description = 'Generated memes'


@admin.register(DiscordServer)
class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'context', 'user_count', 'submission_count', 'meme_count')
    ordering = ('name',)
    search_fields = ('server_id', 'name', 'context__short_name')
    fields = ('server_id', 'name', 'context', 'prefix', 'meme_limit_count', 'meme_limit_time')
    readonly_fields = ('users_link', 'submissions_link', 'memes_link')
    inlines = [DiscordCommandInline]

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields + ('users_link', 'submissions_link', 'memes_link')
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('server_id', 'name')
        return self.readonly_fields

    def users_link(self, obj):
        return list_url(DiscordUser, {
            'discordserveruser__server__server_id': obj.server_id,
        }, obj.user_count)
    users_link.short_description = 'Users'

    def submissions_link(self, obj):
        return list_url(MemeSourceImage, {
            'discordsourceimgsubmission__server_user__server__server_id': obj.server_id,
        }, obj.submission_count)
    submissions_link.short_description = 'Submitted images'

    def memes_link(self, obj):
        return list_url(Meem, {
            'discordmeem__server_user__server__server_id': obj.server_id,
        }, obj.meme_count)
    memes_link.short_description = 'Generated memes'


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_id', 'server_count', 'submission_count', 'meme_count')
    search_fields = ('user_id', 'name')
    ordering = ('name',)
    fields = readonly_fields = ('user_id', 'name', 'submissions_link', 'memes_link')
    inlines = [DiscordServerUserInline]

    def has_add_permission(self, request):
        return False

    def submissions_link(self, obj):
        return list_url(MemeSourceImage, {
            'discordsourceimgsubmission__server_user__user__user_id': obj.user_id,
        }, obj.submission_count)
    submissions_link.short_description = 'Submitted images'

    def memes_link(self, obj):
        return list_url(Meem, {
            'discordmeem__server_user__user__user_id': obj.user_id,
        }, obj.meme_count)
    memes_link.short_description = 'Generated memes'

    def lookup_allowed(self, key, value):
        if key in (
            'discordserveruser__server__server_id',
        ):
            return True
        return super(DiscordUserAdmin, self).lookup_allowed(key, value)
