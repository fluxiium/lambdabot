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
    fields = ('server_admin_url', 'unlimited_memes', 'submission_count', 'meme_count')
    readonly_fields = ('server_admin_url', 'submission_count', 'meme_count')
    ordering = ('server__name',)
    can_delete = False

    def has_add_permission(self, request):
        return False

    def server_admin_url(self, obj):
        return ahref(obj.server.get_admin_url(), obj.server)
    server_admin_url.short_description = 'Server'

    def submission_count(self, obj):
        return obj.get_submissions().count()
    submission_count.short_description = 'Submitted images'

    def meme_count(self, obj):
        return obj.get_memes().count()
    meme_count.short_description = 'Generated memes'


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
    list_display = ('name', 'user_id', 'submission_count', 'meme_count')
    search_fields = ('user_id', 'name')
    ordering = ('name',)
    fields = readonly_fields = ('user_id', 'name', 'srcimg_admin_url', 'meme_count')
    inlines = [DiscordServerUserInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def srcimg_admin_url(self, obj):
        return ahref(obj.get_srcimg_admin_url(), obj.submission_count)
    srcimg_admin_url.short_description = 'Submitted source images'
