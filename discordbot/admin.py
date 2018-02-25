from django.contrib import admin

from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser, DiscordUser, \
    DiscordServerUserPerm, DiscordServerPerm, MurphyRequest, MurphyFacePic


class DiscordCommandInline(admin.TabularInline):
    model = DiscordServer.commands.through
    extra = 0
    verbose_name = "Server command"
    verbose_name_plural = "Server commands"


class DiscordServerPermissionInline(admin.TabularInline):
    model = DiscordServerPerm
    extra = 0


class DiscordServerUserPermissionInline(admin.TabularInline):
    model = DiscordServerUserPerm
    extra = 0


@admin.register(DiscordServer)
class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'context', 'server_id', )
    ordering = ('name',)
    search_fields = ('server_id', 'name', 'context__short_name')
    readonly_fields = ('name',)
    fields = ('server_id', 'name', 'context', 'prefix', 'meme_limit_count', 'meme_limit_time', 'submit_limit_count',
              'submit_limit_time')
    inlines = [DiscordCommandInline, DiscordServerPermissionInline]


@admin.register(DiscordCommand)
class DiscordCommandAdmin(admin.ModelAdmin):
    list_display = ('cmd', 'message')
    ordering = ('cmd',)
    search_fields = ('cmd',)


@admin.register(DiscordServerUser)
class DiscordServerUserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'server')
    search_fields = ('nickname', 'user__user_id', 'user__name', 'server__name', 'server__server_id',
                     'server__context__short_name')
    ordering = ('nickname', 'server')
    fields = ('nickname', 'server', 'meme_limit_count', 'meme_limit_time', 'submit_limit_count', 'submit_limit_time')
    readonly_fields = ('user', 'nickname', 'server')
    inlines = [DiscordServerUserPermissionInline]

    def has_add_permission(self, request):
        return False


# @admin.register(DiscordUser)
# class DiscordUserAdmin(admin.ModelAdmin):
#     list_display = ('name', 'user_id')
#     search_fields = ('user_id', 'name')
#     ordering = ('name',)
#     inlines = [DiscordServerUserInline]
#
#
# @admin.register(DiscordServerPerm)
# class DiscordServerPermissionAdmin(admin.ModelAdmin):
#     list_display = ('server', 'permission', 'allow')
#     search_fields = ('server__server_id', 'server__name', 'server__context__short_name')
#     ordering = ('server', 'permission')
#
#
# @admin.register(DiscordServerUserPerm)
# class DiscordServerUserPermissionAdmin(admin.ModelAdmin):
#     list_display = ('server_user', 'permission', 'allow')
#     search_fields = ('server_user__nickname', 'server_user__user__user_id', 'server_user__user__name',
#                      'server_user__server__name', 'server_user__server__server_id',
#                      'server_user__server__context__short_name')
#     ordering = ('server_user', 'permission')
#
#
# @admin.register(MurphyRequest)
# class MurphyRequestAdmin(admin.ModelAdmin):
#     list_display = ('question', 'face_pic', 'server_user', 'ask_date', 'channel_id', 'processed')
#     search_fields = ('question', 'face_pic', 'server_user__nickname', 'server_user__user__user_id',
#                      'server_user__user__name', 'server_user__server__name', 'server_user__server__server_id',
#                      'server_user__server__context__short_name')
#     ordering = ('-ask_date',)
#
#
# @admin.register(MurphyFacePic)
# class MurphyFacePicAdmin(admin.ModelAdmin):
#     list_display = ('channel_id', 'face_pic', 'last_used')
#     search_fields = ('channel_id', 'face_pic')
#     ordering = ('-last_used',)
