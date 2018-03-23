from django.contrib import admin
from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser, DiscordUser
from memeviewer.admin import ahref


class DiscordCommandInline(admin.TabularInline):
    model = DiscordCommand
    extra = 0


class DiscordServerUserInline(admin.TabularInline):
    model = DiscordServerUser
    extra = 0
    verbose_name_plural = "Server-specific"
    fields = ('server_admin_url', 'unlimited_memes', 'submissions_link', 'memes_link')
    readonly_fields = ('server_admin_url', 'submissions_link', 'memes_link')
    ordering = ('server__name',)
    can_delete = False

    def has_add_permission(self, request):
        return False

    def server_admin_url(self, obj):
        return ahref(obj.server.get_admin_url(), obj.server)
    server_admin_url.short_description = 'Server'

    def submissions_link(self, obj):
        return ahref(obj.get_adminurl_submissions(), obj.submission_count)
    submissions_link.short_description = 'Submitted images'

    def memes_link(self, obj):
        return ahref(obj.get_adminurl_memes(), obj.meme_count)
    memes_link.short_description = 'Generated memes'


@admin.register(DiscordServer)
class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'server_id', 'context', 'submission_count', 'meme_count')
    list_display_links = ('name', 'server_id')
    ordering = ('name',)
    search_fields = ('server_id', 'name', 'context__short_name')
    fields = ('server_id', 'name', 'context', 'prefix', 'meme_limit_count', 'meme_limit_time', 'submission_count', 'meme_count')
    readonly_fields = ('submission_count', 'meme_count')
    inlines = [DiscordCommandInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('server_id', 'name')
        return self.readonly_fields


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_id', 'server_count', 'submission_count', 'meme_count')
    search_fields = ('user_id', 'name')
    ordering = ('name',)
    fields = readonly_fields = ('user_id', 'name', 'srcimg_admin_url', 'meme_count')
    inlines = [DiscordServerUserInline]

    def has_add_permission(self, request):
        return False

    def srcimg_admin_url(self, obj):
        return ahref(obj.get_srcimg_admin_url(), obj.submission_count)
    srcimg_admin_url.short_description = 'Submitted source images'
