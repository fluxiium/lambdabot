from django.contrib import admin
from discordbot.models import DiscordServer, DiscordUser, DiscordChannel, MemeImagePoolOwnership
from memeviewer.models import MemeSourceImage, Meem
from util.admin_utils import list_url


class DiscordChannelInline(admin.StackedInline):
    model = DiscordChannel
    extra = 0
    fields = ('name', 'channel_id', 'image_pools', 'submission_pool', 'disabled_cmds', 'blacklisted', 'submissions_link', 'memes_link')
    readonly_fields = ('submissions_link', 'memes_link')
    ordering = ('name',)

    def submissions_link(self, obj: DiscordChannel):
        return list_url(MemeSourceImage, {
            'discordsourceimgsubmission__discord_channel': obj.channel_id,
        }, MemeSourceImage.objects.filter(discordsourceimgsubmission__discord_channel=obj).count())
    submissions_link.short_description = 'Submitted source images'

    def memes_link(self, obj: DiscordChannel):
        return list_url(Meem, {
            'discordmeem__discord_channel': obj.channel_id,
        }, Meem.objects.filter(discordmeem__discord_channel=obj).count())
    memes_link.short_description = 'Generated memes'


@admin.register(DiscordServer)
class DiscordServerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'server_id', 'blacklisted')
    ordering = ('name',)
    search_fields = ('server_id', 'name',)
    readonly_fields = ('submissions_link', 'memes_link')
    fields = ('name', 'server_id', 'prefix', 'disabled_cmds', 'blacklisted', 'submissions_link', 'memes_link')
    inlines = [DiscordChannelInline]

    def submissions_link(self, obj: DiscordServer):
        return list_url(MemeSourceImage, {
            'discordsourceimgsubmission__discord_channel__server': obj.server_id,
        }, MemeSourceImage.objects.filter(discordsourceimgsubmission__discord_channel__server=obj).count())
    submissions_link.short_description = 'Submitted source images'

    def memes_link(self, obj: DiscordServer):
        return list_url(Meem, {
            'discordmeem__discord_channel__server': obj.server_id,
        }, Meem.objects.filter(discordmeem__discord_channel__server=obj).count())
    memes_link.short_description = 'Generated memes'


class MemeImagePoolOwnershipInline(admin.TabularInline):
    model = MemeImagePoolOwnership
    extra = 0
    fields = ('owner', 'image_pool', 'shared_with', 'moderators', 'publish_requested')
    filter_vertical = ('shared_with', 'moderators')


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user_id', 'blacklisted')
    search_fields = ('user_id', 'name')
    ordering = ('name',)
    readonly_fields = ('submissions_link', 'memes_link')
    fields = ('user_id', 'name', 'blacklisted', 'submissions_link', 'memes_link')
    # inlines = [MemeImagePoolOwnershipInline]

    def submissions_link(self, obj: DiscordUser):
        return list_url(MemeSourceImage, {
            'discordsourceimgsubmission__discord_user': obj.user_id,
        }, MemeSourceImage.objects.filter(discordsourceimgsubmission__discord_user=obj).count())
    submissions_link.short_description = 'Submitted source images'

    def memes_link(self, obj: DiscordUser):
        return list_url(Meem, {
            'discordmeem__discord_user': obj.user_id,
        }, Meem.objects.filter(discordmeem__discord_user=obj).count())
    memes_link.short_description = 'Generated memes'

    def lookup_allowed(self, key, value):
        return True
