from django.contrib import admin
from django.utils.safestring import mark_safe
from discordbot.models import DiscordMeem, DiscordSourceImgSubmission
from facebookbot.models import FacebookMeem
from lamdabotweb.settings import USERNAME_TWITTER
from memeviewer.models import Meem, MemeTemplate, MemeTemplateSlot, MemeContext, MemeSourceImage, MemeSourceImageInSlot
from twitterbot.models import TwitterMeem


class SocialLinkInline(admin.TabularInline):
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        return False


class FacebookInline(SocialLinkInline):
    model = FacebookMeem
    verbose_name_plural = "Facebook"
    fields = readonly_fields = ('facebook_url',)

    def facebook_url(self, obj):
        return mark_safe('<a href="https://facebook.com/{0}" target="_blank">Show associated facebook post</a>'.format(obj.post))
    facebook_url.short_description = 'Facebook post'


class TwitterInline(SocialLinkInline):
    model = TwitterMeem
    verbose_name_plural = "Twitter"

    fields = readonly_fields = ('twitter_url',)

    def twitter_url(self, obj):
        return mark_safe('<a href="https://twitter.com/{0}/status/{1}" target="_blank">Show associated twitter post</a>'.format(
            USERNAME_TWITTER, obj.post
        ))
    twitter_url.short_description = 'Twitter post'


class DiscordInline(SocialLinkInline):
    model = DiscordMeem
    fields = readonly_fields = ('user_admin_url', 'server_admin_url', 'channel_id')
    verbose_name_plural = "Discord"

    def user_admin_url(self, obj):
        return mark_safe('<a href="{0}">{1}</a>'.format(
            obj.server_user.user.get_admin_url(), obj.server_user.nickname
        ))
    user_admin_url.short_description = 'User'

    def server_admin_url(self, obj):
        return mark_safe('<a href="{0}">{1}</a>'.format(
            obj.server_user.server.get_admin_url(), obj.server_user.server
        ))
    server_admin_url.short_description = 'Server'


class MemeTemplateSlotInline(admin.TabularInline):
    model = MemeTemplateSlot
    extra = 0


class MemeSourceImageInSlotInline(admin.TabularInline):
    model = MemeSourceImageInSlot
    extra = 0
    verbose_name_plural = "Source images"
    fields = readonly_fields = ('slot', 'admin_url')
    can_delete = False

    def has_add_permission(self, request):
        return False

    def admin_url(self, obj):
        return mark_safe('<a href="{0}">{1}</a>'.format(
            obj.source_image.get_admin_url(), obj.source_image.friendly_name or obj.source_image.name
        ))
    admin_url.short_description = 'Source image'


class DiscordSourceImgSubmissionInline(admin.TabularInline):
    model = DiscordSourceImgSubmission
    extra = 0
    verbose_name_plural = "Discord source image submission"
    fields = readonly_fields = ('user_admin_url', 'server_admin_url')
    can_delete = False

    def has_add_permission(self, request):
        return False

    def user_admin_url(self, obj):
        return mark_safe('<a href="{0}">{1}</a>'.format(
            obj.server_user.user.get_admin_url(), obj.server_user.nickname
        ))
    user_admin_url.short_description = 'User'

    def server_admin_url(self, obj):
        return mark_safe('<a href="{0}">{1}</a>'.format(
            obj.server_user.server.get_admin_url(), obj.server_user.server
        ))
    server_admin_url.short_description = 'Server'


@admin.register(Meem)
class MeemAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'number', 'meme_id', 'template_link', 'context_link', 'gen_date')
    list_display_links = ('thumbnail', 'number', 'meme_id',)
    list_filter = ('context_link',)
    search_fields = ('number', 'meme_id', 'template_link__name')
    ordering = ('-number', 'meme_id')
    inlines = [MemeSourceImageInSlotInline, FacebookInline, TwitterInline, DiscordInline]
    readonly_fields = ('number', 'meme_id', 'template_admin_url', 'context_link', 'gen_date', 'image', 'meme_url')
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    def meme_url(self, obj):
        return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(obj.get_info_url(), "Show meme page"))
    meme_url.short_description = 'Meme page'

    def image(self, obj):
        return mark_safe('<a href="{0}" target="_blank"><img src="{1}" width="350"></a>'.format(obj.get_info_url(), obj.get_url()))
    image.short_description = 'Image'

    def thumbnail(self, obj):
        return mark_safe('<img src="{}" width="150">'.format(obj.get_url()))
    thumbnail.short_description = 'Thumbnail'

    def template_admin_url(self, obj):
        return mark_safe('<a href="{0}">{1}</a>'.format(
            obj.template_link.get_admin_url(), obj.template_link.friendly_name or obj.template_link.name
        ))
    template_admin_url.short_description = 'Template'

    def lookup_allowed(self, key, value):
        if key in (
            'memesourceimageinslot__source_image__name__exact',
            'template_link__name__exact',
            'discordmeem__server_user__user__user_id__exact',
            'discordmeem__server_user__server__server_id__exact'
        ):
            return True


@admin.register(MemeSourceImage)
class MemeSourceImageAdmin(admin.ModelAdmin):
    list_display = ('accepted', 'thumbnail', 'name', 'friendly_name', 'contexts_string', 'add_date')
    list_display_links = ('thumbnail', 'name')
    list_filter = ('accepted', 'contexts',)
    search_fields = ('name', 'friendly_name')
    ordering = ('-add_date', 'name',)
    inlines = [DiscordSourceImgSubmissionInline]
    actions = ['accept']

    fields = ('name', 'friendly_name', 'image_file', 'contexts', 'accepted',)

    def thumbnail(self, obj):
        return mark_safe('<img src="{}" width="150">'.format(obj.get_image_url()))
    thumbnail.short_description = 'Thumbnail'

    def accept(self, request, queryset):
        queryset.update(accepted=True)
    accept.short_description = "Approve selected source images"

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields + ('add_date', 'memes_admin_url',)
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('name', 'add_date', 'memes_admin_url')
        return self.readonly_fields

    def memes_admin_url(self, obj):
        return mark_safe('<a href="{0}">Show memes using this source image</a>'.format(obj.get_memes_admin_url()))
    memes_admin_url.short_description = 'Memes'

    def lookup_allowed(self, key, value):
        if key in (
            'discordsourceimgsubmission__server_user__user__user_id__exact',
        ):
            return True


@admin.register(MemeTemplate)
class MemeTemplateAdmin(admin.ModelAdmin):
    list_display = ('accepted', 'thumbnail', 'name', 'friendly_name', 'contexts_string', 'add_date', 'preview_url')
    list_display_links = ('thumbnail', 'name')
    list_filter = ('accepted', 'contexts',)
    search_fields = ('name', 'friendly_name')
    ordering = ('-add_date', 'name')
    inlines = [MemeTemplateSlotInline]
    actions = ['accept']

    fields = ('name', 'friendly_name', 'image_file', 'bg_image_file', 'bg_color', 'contexts', 'accepted',)

    def preview_url(self, obj):
        return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(
            obj.get_preview_url(), "Generate meme using this template"
        ))
    preview_url.short_description = 'Preview'

    def thumbnail(self, obj):
        return mark_safe('<img src="{}" width="150">'.format(obj.get_image_url()))
    thumbnail.short_description = 'Thumbnail'

    def accept(self, request, queryset):
        queryset.update(accepted=True)
    accept.short_description = "Approve selected templates"

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields + ('add_date', 'preview_url', 'memes_admin_url',)
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('name', 'add_date', 'preview_url', 'memes_admin_url')
        return self.readonly_fields

    def memes_admin_url(self, obj):
        return mark_safe('<a href="{0}">Show memes using this template</a>'.format(obj.get_memes_admin_url()))
    memes_admin_url.short_description = 'Memes'


@admin.register(MemeContext)
class MemeContextAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'reset_url')
    search_fields = ('short_name', 'name')
    fields = ('name', 'short_name', 'reset_url')
    readonly_fields = ('reset_url',)
    ordering = ('name',)

    def reset_url(self, obj):
        return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(obj.get_reset_url(), "Reset"))
    reset_url.short_description = 'Reset image queue'

    def get_model_perms(self, request):
        return {}

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('short_name',)
        return self.readonly_fields
