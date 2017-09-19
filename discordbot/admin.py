from django.contrib import admin

from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser, DiscordUser, \
    DiscordServerUserPermission, DiscordServerPermission


class DiscordServerPermissionInline(admin.TabularInline):
    model = DiscordServerPermission
    extra = 0


class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('server_id', 'name', 'context')
    ordering = ('name', 'server_id')
    search_fields = ('server_id', 'name', 'context__short_name')
    inlines = [DiscordServerPermissionInline]

admin.site.register(DiscordServer, DiscordServerAdmin)


class DiscordCommandAdmin(admin.ModelAdmin):
    list_display = ('cmd', 'help', 'message')
    ordering = ('cmd',)
    search_fields = ('cmd',)


admin.site.register(DiscordCommand, DiscordCommandAdmin)


class DiscordServerUserInline(admin.TabularInline):
    model = DiscordServerUser
    extra = 0


class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name')
    search_fields = ('user_id', 'name')
    inlines = [DiscordServerUserInline]

admin.site.register(DiscordUser, DiscordUserAdmin)


class DiscordServerUserPermissionInline(admin.TabularInline):
    model = DiscordServerUserPermission
    extra = 0


class DiscordServerUserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'user', 'server')
    search_fields = ('nickname', 'user__user_id', 'user__name', 'server__name')
    inlines = [DiscordServerUserPermissionInline]

admin.site.register(DiscordServerUser, DiscordServerUserAdmin)
