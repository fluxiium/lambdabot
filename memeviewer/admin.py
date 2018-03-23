from django.contrib import admin
from django.utils.safestring import mark_safe
from discordbot.models import DiscordMeem, DiscordSourceImgSubmission
from facebookbot.models import FacebookMeem
from lamdabotweb.settings import USERNAME_TWITTER
from memeviewer.models import Meem, MemeTemplate, MemeTemplateSlot, MemeContext, MemeSourceImage
from twitterbot.models import TwitterMeem


def htmlimg(url, mw=150, mh=150):
    return mark_safe('<img src="{0}" style="max-width: {1}px; max-height: {2}px;">'.format(url, mw, mh))


def ahref(url, text, newtab=False):
    return mark_safe('<a href="{0}"{1}>{2}</a>'.format(url, newtab and ' target="_blank"' or '', text))


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
        return ahref('https://facebook.com/' + obj.post, 'Show associated facebook post', True)
    facebook_url.short_description = 'Facebook post'


class TwitterInline(SocialLinkInline):
    model = TwitterMeem
    verbose_name_plural = "Twitter"

    fields = readonly_fields = ('twitter_url',)

    def twitter_url(self, obj):
        return ahref('https://twitter.com/{0}/status/{1}'.format(USERNAME_TWITTER, obj.post, True),
                     'Show associated twitter post')
    twitter_url.short_description = 'Twitter post'


class DiscordInline(SocialLinkInline):
    model = DiscordMeem
    fields = readonly_fields = ('user_admin_url', 'server_admin_url', 'channel_id')
    verbose_name_plural = "Discord"

    def user_admin_url(self, obj):
        return ahref(obj.server_user.user.get_admin_url(), obj.server_user.nickname)
    user_admin_url.short_description = 'User'

    def server_admin_url(self, obj):
        return ahref(obj.server_user.server.get_admin_url(), obj.server_user.server)
    server_admin_url.short_description = 'Server'


class MemeTemplateSlotInline(admin.TabularInline):
    model = MemeTemplateSlot
    extra = 0


class DiscordSourceImgSubmissionInline(admin.TabularInline):
    model = DiscordSourceImgSubmission
    extra = 0
    verbose_name_plural = "Discord source image submission"
    fields = readonly_fields = ('user_admin_url', 'server_admin_url')
    can_delete = False

    def has_add_permission(self, request):
        return False

    def user_admin_url(self, obj):
        return ahref(obj.server_user.user.get_admin_url(), obj.server_user.nickname)
    user_admin_url.short_description = 'User'

    def server_admin_url(self, obj):
        return ahref(obj.server_user.server.get_admin_url(), obj.server_user.server)
    server_admin_url.short_description = 'Server'


@admin.register(Meem)
class MeemAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'number', 'meme_id', 'template_link', 'context_link', 'gen_date')
    list_display_links = ('thumbnail', 'number', 'meme_id',)
    list_filter = ('context_link',)
    search_fields = ('number', 'meme_id', 'template_link__name', 'source_images')
    ordering = ('-number', 'meme_id')
    inlines = [FacebookInline, TwitterInline, DiscordInline]
    readonly_fields = ('number', 'meme_id', 'template_admin_url', 'sourceimg_admin_urls', 'context_link', 'gen_date',
                       'image', 'meme_url')
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    def meme_url(self, obj):
        return ahref(obj.get_info_url(), "Show meme page")
    meme_url.short_description = 'Meme page'

    def image(self, obj):
        return ahref(obj.get_url(), htmlimg(obj.get_url(), mw=600, mh=400))
    image.short_description = 'Image'

    def thumbnail(self, obj):
        return htmlimg(obj.get_url(), mw=150, mh=150)
    thumbnail.short_description = 'Thumbnail'

    def template_admin_url(self, obj):
        return ahref(obj.template_link.get_admin_url(), obj.template_link)
    template_admin_url.short_description = 'Template'

    def sourceimg_admin_urls(self, obj):
        html = ""
        for srcimg in obj.get_sourceimgs():
            html += ahref(srcimg.get_admin_url(), srcimg) + '<br>'
        return mark_safe(html)
    sourceimg_admin_urls.short_description = 'Source images'

    def lookup_allowed(self, key, value):
        if key in (
            'source_images__contains',
            'template_link__name__exact',
        ):
            return True
        return super(MeemAdmin, self).lookup_allowed(key, value)


@admin.register(MemeSourceImage)
class MemeSourceImageAdmin(admin.ModelAdmin):
    list_display = ('accepted', 'thumbnail', 'name', 'friendly_name', 'contexts_string', 'change_date')
    list_display_links = ('thumbnail', 'name')
    list_filter = ('accepted', 'contexts',)
    search_fields = ('name', 'friendly_name')
    ordering = ('-change_date',)
    inlines = [DiscordSourceImgSubmissionInline]
    actions = ['accept', 'reject',]

    fields = ('name', 'friendly_name', 'image_file', 'contexts', 'accepted',)

    def image(self, obj):
        return ahref(obj.get_image_url(), htmlimg(obj.get_image_url(), mw=600, mh=400))
    image.short_description = 'Preview'

    def thumbnail(self, obj):
        return htmlimg(obj.get_image_url(), mw=150, mh=150)
    thumbnail.short_description = 'Thumbnail'

    def accept(self, request, queryset):
        queryset.update(accepted=True)
        for img in queryset:
            img.enqueue()
    accept.short_description = "Approve selected source images"

    def reject(self, request, queryset):
        queryset.update(accepted=False)
        for img in queryset:
            img.enqueue()
    reject.short_description = "Reject selected source images"

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields + ('image', 'add_date', 'change_date', 'memes_admin_url',)
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('name', 'add_date', 'change_date', 'image', 'memes_admin_url')
        return self.readonly_fields

    def memes_admin_url(self, obj):
        return ahref(obj.get_memes_admin_url(), 'Show memes using this source image')
    memes_admin_url.short_description = 'Memes'

    def lookup_allowed(self, key, value):
        if key in (
            'discordsourceimgsubmission__server_user__user__user_id__exact',
        ):
            return True
        return super(MemeSourceImageAdmin, self).lookup_allowed(key, value)

    def save_related(self, request, form, formsets, change):
        admin.ModelAdmin.save_related(self, request, form, formsets, change)
        form.instance.enqueue()


@admin.register(MemeTemplate)
class MemeTemplateAdmin(admin.ModelAdmin):
    list_display = ('accepted', 'thumbnail', 'name', 'friendly_name', 'contexts_string', 'change_date')
    list_display_links = ('thumbnail', 'name')
    list_filter = ('accepted', 'contexts',)
    search_fields = ('name', 'friendly_name')
    ordering = ('-change_date',)
    inlines = [MemeTemplateSlotInline]
    actions = ['accept', 'reject',]

    def preview_url(self, obj):
        return ahref(obj.get_preview_url(), "Generate meme using this template")
    preview_url.short_description = 'Preview'

    def fg_image(self, obj):
        return ahref(obj.get_image_url(), htmlimg(obj.get_image_url(), mw=600, mh=400))
    fg_image.short_description = ''

    def bg_image(self, obj):
        return ahref(obj.get_bgimage_url(), htmlimg(obj.get_bgimage_url(), mw=600, mh=400))
    bg_image.short_description = ''

    def thumbnail(self, obj):
        return htmlimg(obj.image_file and obj.get_image_url() or obj.get_bgimage_url(), mw=150, mh=150)
    thumbnail.short_description = 'Thumbnail'

    def accept(self, request, queryset):
        queryset.update(accepted=True)
        for img in queryset:
            img.enqueue()
    accept.short_description = "Approve selected templates"

    def reject(self, request, queryset):
        queryset.update(accepted=False)
        for img in queryset:
            img.enqueue()
    reject.short_description = "Reject selected templates"

    def get_fields(self, request, obj=None):
        fields = ('name', 'friendly_name', 'bg_image_file',)
        if obj and obj.get_bgimage_url():
            fields += ('bg_image',)
        fields += ('image_file',)
        if obj and obj.get_image_url():
            fields += ('fg_image',)
        fields += ('bg_color', 'contexts', 'accepted',)
        if obj:
            fields += ('add_date', 'change_date', 'preview_url', 'memes_admin_url',)
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('name', 'add_date', 'change_date', 'preview_url', 'memes_admin_url',
                                           'fg_image', 'bg_image')
        return self.readonly_fields

    def memes_admin_url(self, obj):
        return ahref(obj.get_memes_admin_url(), 'Show memes using this template')
    memes_admin_url.short_description = 'Memes'

    def save_related(self, request, form, formsets, change):
        admin.ModelAdmin.save_related(self, request, form, formsets, change)
        form.instance.enqueue()


@admin.register(MemeContext)
class MemeContextAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'is_public', 'meme_count', 'reset_url')
    search_fields = ('short_name', 'name')
    fields = ('short_name', 'name', 'recent_threshold', 'is_public', 'meme_count')
    readonly_fields = ('meme_count', 'reset_url',)
    ordering = ('name',)

    def reset_url(self, obj):
        return ahref(obj.get_reset_url(), "Reset")
    reset_url.short_description = 'Reset image queue'

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields + ('reset_url',)
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('short_name',)
        return self.readonly_fields
