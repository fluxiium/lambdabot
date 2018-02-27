from django.contrib import admin
from django.utils.safestring import mark_safe

from discordbot.models import DiscordMeem, DiscordSourceImgSubmission
from facebookbot.models import FacebookMeem
from memeviewer.models import Meem, ImageInContext, MemeTemplate, \
    MemeTemplateSlot, MemeContext, MemeSourceImage, MemeSourceImageInSlot
from twitterbot.models import TwitterMeem


class SocialLinkInline(admin.TabularInline):
    extra = 0
    readonly_fields = ('meme', 'post')
    can_delete = False

    def has_add_permission(self, request):
        return False


class FacebookInline(SocialLinkInline):
    model = FacebookMeem
    verbose_name_plural = "Facebook post"


class TwitterInline(SocialLinkInline):
    model = TwitterMeem
    verbose_name_plural = "Twitter post"


class DiscordInline(SocialLinkInline):
    model = DiscordMeem
    readonly_fields = ('meme', 'server_user', 'channel_id')
    verbose_name_plural = "Discord post"


class MemeTemplateSlotInline(admin.TabularInline):
    model = MemeTemplateSlot
    extra = 0


class MemeSourceImageInSlotInline(admin.TabularInline):
    model = MemeSourceImageInSlot
    extra = 0
    verbose_name_plural = "Source images"
    readonly_fields = ('slot', 'source_image')
    can_delete = False

    def has_add_permission(self, request):
        return False


class DiscordSourceImgSubmissionInline(admin.TabularInline):
    model = DiscordSourceImgSubmission
    extra = 0
    verbose_name_plural = "Discord source image submission"
    readonly_fields = ('server_user',)
    can_delete = False

    def has_add_permission(self, request):
        return False


@admin.register(Meem)
class MeemAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'number', 'meme_id', 'template_link', 'context_link', 'gen_date', 'meme_url')
    list_display_links = ('thumbnail', 'number', 'meme_id',)
    list_filter = ('context_link', 'memesourceimageinslot__source_image')
    search_fields = ('number', 'meme_id', 'template_link__name')
    ordering = ('-number', 'meme_id')
    inlines = [MemeSourceImageInSlotInline, FacebookInline, TwitterInline, DiscordInline]
    readonly_fields = ('number', 'meme_id', 'template_link', 'context_link', 'gen_date', 'image', 'meme_url')
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    def meme_url(self, obj):
        return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(obj.get_info_url(), "Meme page"))
    meme_url.short_description = 'Page'

    def image(self, obj):
        return mark_safe('<a href="{0}" target="_blank"><img src="{1}" width="350"></a>'.format(obj.get_info_url(), obj.get_url()))
    image.short_description = 'Image'

    def thumbnail(self, obj):
        return mark_safe('<img src="{}" width="150">'.format(obj.get_url()))
    thumbnail.short_description = 'Thumbnail'


@admin.register(MemeSourceImage)
class MemeSourceImageAdmin(admin.ModelAdmin):
    list_display = ('accepted', 'thumbnail', 'name', 'friendly_name', 'contexts_string', 'add_date')
    list_display_links = ('thumbnail', 'name')
    list_filter = ('accepted', 'contexts',)
    search_fields = ('name', 'friendly_name')
    ordering = ('-add_date', 'name',)
    inlines = [DiscordSourceImgSubmissionInline]
    actions = ['accept']

    fields = ('name', 'friendly_name', 'image_file', 'contexts', 'accepted', 'add_date')

    def thumbnail(self, obj):
        return mark_safe('<img src="{}" width="150">'.format(obj.get_image_url()))
    thumbnail.short_description = 'Thumbnail'

    def accept(self, request, queryset):
        queryset.update(accepted=True)
    accept.short_description = "Approve selected source images"


@admin.register(MemeTemplate)
class MemeTemplateAdmin(admin.ModelAdmin):
    list_display = ('accepted', 'thumbnail', 'name', 'friendly_name', 'contexts_string', 'add_date', 'preview_url')
    list_display_links = ('thumbnail', 'name')
    list_filter = ('accepted', 'contexts',)
    search_fields = ('name', 'friendly_name')
    ordering = ('-add_date', 'name')
    inlines = [MemeTemplateSlotInline]
    actions = ['accept']

    readonly_fields = ['preview_url']
    fields = ('name', 'friendly_name', 'image_file', 'bg_image_file', 'bg_color',
              'contexts', 'accepted', 'add_date', 'preview_url')

    def preview_url(self, obj):
        return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(obj.get_preview_url(), "Preview"))
    preview_url.short_description = 'Preview'

    def thumbnail(self, obj):
        return mark_safe('<img src="{}" width="150">'.format(obj.get_image_url()))
    thumbnail.short_description = 'Thumbnail'

    def accept(self, request, queryset):
        queryset.update(accepted=True)
    accept.short_description = "Approve selected templates"


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
