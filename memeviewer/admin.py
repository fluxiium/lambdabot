from django.contrib import admin
from django.utils.safestring import mark_safe
from discordbot.models import DiscordMeem, DiscordSourceImgSubmission, DiscordUser, DiscordServer
from facebookbot.models import FacebookMeem
from lamdabotweb.settings import USERNAME_TWITTER
from memeviewer.models import Meem, MemeTemplate, MemeTemplateSlot, MemeContext, MemeSourceImage, \
    MemeSourceImageInContext, MemeTemplateInContext
from twitterbot.models import TwitterMeem
from util.admin_utils import ahref, htmlimg, object_url, list_url


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
    fields = readonly_fields = ('user_link', 'server_link', 'channel_id')
    verbose_name_plural = "Discord"

    def user_link(self, obj):
        return object_url(DiscordUser, obj.server_user.user_id, obj.server_user.user)
    user_link.short_description = 'User'

    def server_link(self, obj):
        return object_url(DiscordServer, obj.server_user.server_id, obj.server_user.server)
    server_link.short_description = 'Server'


@admin.register(Meem)
class MeemAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'number', 'template_admin_url', 'sourceimg_admin_urls', 'context_admin_url', 'gen_date')
    list_display_links = ('thumbnail', 'number')
    list_filter = ('context_link',)
    search_fields = ('number', 'meme_id', 'template_link__name', 'source_images')
    ordering = ('-number', 'meme_id')
    inlines = [FacebookInline, TwitterInline, DiscordInline]
    readonly_fields = ('number', 'meme_id', 'template_admin_url', 'sourceimg_admin_urls', 'context_admin_url', 'gen_date',
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
        return object_url(MemeTemplate, obj.template_link.name, obj.template_link)
    template_admin_url.short_description = 'Template'

    def sourceimg_admin_urls(self, obj):
        html = ""
        for srcimg in obj.get_sourceimgs():
            html += object_url(MemeSourceImage, srcimg.name, srcimg) + "<br>"
        return mark_safe(html)
    sourceimg_admin_urls.short_description = 'Source images'

    def context_admin_url(self, obj):
        return object_url(MemeContext, obj.context_link.short_name, obj.context_link)
    context_admin_url.short_description = 'Context'

    def lookup_allowed(self, key, value):
        if key in (
            'source_images__contains',
            'template_link__name__exact',
            'discordmeem__server_user__user__user_id',
            'discordmeem__server_user__server__server_id'
        ):
            return True
        return super(MeemAdmin, self).lookup_allowed(key, value)


class MemeImageAdmin(admin.ModelAdmin):
    list_display = ('accepted', 'thumbnail', '__str__', 'context_links', 'memes_link', 'change_date')
    list_display_links = ('thumbnail', '__str__')
    list_filter = ('accepted', 'contexts',)
    fields = ('name', 'friendly_name', 'image', 'contexts', 'accepted', 'add_date', 'change_date', 'memes_link',
              'preview_url',)
    readonly_fields = ('name', 'add_date', 'change_date', 'image', 'memes_link', 'preview_url')
    search_fields = ('name', 'friendly_name')
    ordering = ('-change_date',)
    actions = ['accept', 'reject']

    def has_add_permission(self, request):
        return False

    def context_links(self, obj):
        cs = obj.contexts.all()
        if cs.count() > 0:
            html = ""
            for c in obj.contexts.all():
                html += object_url(MemeContext, c.short_name, c) + "<br>"
            return mark_safe(html)
        else:
            return list_url(MemeContext, {}, "(all)")
    context_links.short_description = 'Contexts'

    def preview_url(self, obj):
        return ahref(obj.get_preview_url(), "Generate meme using this image")
    preview_url.short_description = 'Preview'

    def accept(self, request, queryset):
        queryset.update(accepted=True)
        for img in queryset:
            img.clean()
            img.enqueue()
    accept.short_description = "Approve selected images"

    def reject(self, request, queryset):
        queryset.update(accepted=False)
        for img in queryset:
            img.clean()
            img.enqueue()
    reject.short_description = "Reject selected images"

    def save_related(self, request, form, formsets, change):
        admin.ModelAdmin.save_related(self, request, form, formsets, change)
        form.instance.enqueue()


class MemeImageInContextInline(admin.TabularInline):
    extra = 0
    verbose_name_plural = "In context"
    fields = ('context_link', 'memes_link', 'queued')
    readonly_fields = ('context_link', 'memes_link')
    can_delete = False

    def has_add_permission(self, request):
        return False

    def context_link(self, obj):
        return object_url(MemeContext, obj.context.short_name, obj.context)
    context_link.short_description = 'Context'

    def memes_link(self, obj):
        return list_url(Meem, {
            'source_images__contains': '%22' + obj.image.name + '%22',
            'context_link__short_name__exact': obj.context.short_name,
        }, obj.random_usages)
    memes_link.short_description = 'Memes'


class MemeSourceImageInContextInline(MemeImageInContextInline):
    model = MemeSourceImageInContext


class DiscordSourceImgSubmissionInline(admin.TabularInline):
    model = DiscordSourceImgSubmission
    extra = 0
    verbose_name_plural = "Discord source image submission"
    fields = readonly_fields = ('user_link', 'server_link')
    can_delete = False

    def has_add_permission(self, request):
        return False

    def user_link(self, obj):
        return object_url(DiscordUser, obj.server_user.user_id, obj.server_user.user)
    user_link.short_description = 'User'

    def server_link(self, obj):
        return object_url(DiscordServer, obj.server_user.server_id, obj.server_user.server)
    server_link.short_description = 'Server'


@admin.register(MemeSourceImage)
class MemeSourceImageAdmin(MemeImageAdmin):
    inlines = [MemeSourceImageInContextInline, DiscordSourceImgSubmissionInline]

    def image(self, obj):
        return ahref(obj.get_image_url(), htmlimg(obj.get_image_url(), mw=600, mh=400))
    image.short_description = 'Image'

    def thumbnail(self, obj):
        return htmlimg(obj.get_image_url(), mw=150, mh=150)
    thumbnail.short_description = 'Thumbnail'

    def memes_link(self, obj):
        return list_url(Meem, {
            'source_images__contains': '%22' + obj.name + '%22'
        }, obj.meme_count)
    memes_link.short_description = 'Memes'

    def lookup_allowed(self, key, value):
        if key in (
            'discordsourceimgsubmission__server_user__user__user_id',
            'discordsourceimgsubmission__server_user__server__server_id',
        ):
            return True
        return super(MemeSourceImageAdmin, self).lookup_allowed(key, value)


class MemeTemplateSlotInline(admin.TabularInline):
    model = MemeTemplateSlot
    extra = 0


class MemeTemplateInContextInline(MemeImageInContextInline):
    model = MemeTemplateInContext


@admin.register(MemeTemplate)
class MemeTemplateAdmin(MemeImageAdmin):
    inlines = [MemeTemplateInContextInline]

    def image(self, obj):
        return mark_safe(
            ahref(obj.get_image_url(), htmlimg(obj.get_image_url(), mw=600, mh=400)) + " " +
            ahref(obj.get_bgimage_url(), htmlimg(obj.get_bgimage_url(), mw=600, mh=400))
        )
    image.short_description = 'Image(s)'

    def thumbnail(self, obj):
        return htmlimg(obj.image_file and obj.get_image_url() or obj.get_bgimage_url(), mw=150, mh=150)
    thumbnail.short_description = 'Thumbnail'

    def memes_link(self, obj):
        return list_url(Meem, {
            'template_link__name': obj.name
        }, obj.meme_count)
    memes_link.short_description = 'Memes'


@admin.register(MemeContext)
class MemeContextAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'is_public', 'memes_link', 'reset_url')
    search_fields = ('short_name', 'name')
    fields = ('short_name', 'name', 'recent_threshold', 'is_public', 'memes_link')
    readonly_fields = ('memes_link', 'reset_url',)
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

    def memes_link(self, obj):
        return list_url(Meem, {
            'context_link__short_name__exact': obj.short_name
        }, obj.meme_count)
    memes_link.short_description = 'Memes'
