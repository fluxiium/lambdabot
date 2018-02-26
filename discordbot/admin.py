from django.contrib import admin

from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser, DiscordUser, MurphyRequest, MurphyFacePic


class DiscordCommandInline(admin.TabularInline):
    model = DiscordCommand
    extra = 0


class DiscordServerUserInline(admin.TabularInline):
    model = DiscordServerUser
    extra = 0
    fields = ('server', 'meme_limit_count', 'meme_limit_time', 'submit_limit_count', 'submit_limit_time')
    readonly_fields = ('server',)
    ordering = ('server__name',)
    can_delete = False

    def has_add_permission(self, request):
        return False


@admin.register(DiscordServer)
class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'server_id', 'context')
    list_display_links = ('name', 'server_id')
    ordering = ('name',)
    search_fields = ('server_id', 'name', 'context__short_name')
    fields = ('server_id', 'name', 'context', 'prefix', 'meme_limit_count', 'meme_limit_time', 'submit_limit_count',
              'submit_limit_time')
    inlines = [DiscordCommandInline]


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_id')
    search_fields = ('user_id', 'name')
    ordering = ('name',)
    readonly_fields = ('user_id', 'name')
    inlines = [DiscordServerUserInline]


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
