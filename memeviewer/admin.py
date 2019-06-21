from django.contrib import admin
from django.utils.safestring import mark_safe

from discordbot.admin import MemeImagePoolOwnershipInline
from discordbot.models import DiscordMeem, DiscordSourceImgSubmission, DiscordUser, DiscordServer
from facebookbot.models import FacebookMeem, FacebookPage
from memeviewer.models import Meem, MemeTemplate, MemeTemplateSlot, MemeSourceImage, MemeImagePool, QueuedMemeImage
from twitterbot.models import TwitterMeem, TwitterPage
from util.admin_utils import ahref, htmlimg, object_url, list_url


class SocialLinkInline(admin.TabularInline):
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        return False


class FacebookInline(SocialLinkInline):
    model = FacebookMeem
    verbose_name_plural = "Facebook"
    fields = readonly_fields = ('facebook_url', 'page_admin_url')

    def facebook_url(self, obj: FacebookMeem):
        return ahref('https://facebook.com/' + obj.post, 'See post', True)
    facebook_url.short_description = 'Facebook post'

    def page_admin_url(self, obj: FacebookMeem):
        return object_url(FacebookPage, obj.page.page_id, obj.page)
    page_admin_url.short_description = 'Facebook page'


class TwitterInline(SocialLinkInline):
    model = TwitterMeem
    verbose_name_plural = "Twitter"

    fields = readonly_fields = ('twitter_url', 'page_admin_url')

    def twitter_url(self, obj: TwitterMeem):
        return ahref('https://twitter.com/statuses/' + obj.post, 'See post', True)
    twitter_url.short_description = 'Twitter post'

    def page_admin_url(self, obj: TwitterMeem):
        return object_url(TwitterPage, obj.page.pk, obj.page)
    page_admin_url.short_description = 'Twitter page'


class DiscordInline(SocialLinkInline):
    model = DiscordMeem
    fields = readonly_fields = ('user_link', 'server_link')
    verbose_name_plural = "Discord"

    def user_link(self, obj: DiscordMeem):
        return object_url(DiscordUser, obj.discord_user.user_id, obj.discord_user)
    user_link.short_description = 'User'

    def server_link(self, obj: DiscordMeem):
        return object_url(DiscordServer, obj.discord_channel.server.server_id, obj.discord_channel)
    server_link.short_description = 'Channel'


class DiscordMeemInline(DiscordInline):
    model = DiscordMeem


class DiscordSourceImgSubmissionInline(DiscordInline):
    model = DiscordSourceImgSubmission


@admin.register(Meem)
class MeemAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'number', 'template_admin_url', 'sourceimg_admin_urls', 'gen_date')
    list_display_links = ('thumbnail', 'number')
    search_fields = ('number', 'meme_id', 'template_link__name', 'source_images')
    ordering = ('-number',)
    inlines = [FacebookInline, TwitterInline, DiscordInline]
    fields = readonly_fields = ('number', 'meme_id', 'template_admin_url', 'sourceimg_admin_urls', 'gen_date', 'image')

    def has_add_permission(self, request):
        return False

    def image(self, obj: Meem):
        return ahref(obj.url, htmlimg(obj.url, mw=600, mh=400))
    image.short_description = 'Image'

    def thumbnail(self, obj: Meem):
        return htmlimg(obj.url, mw=150, mh=150)
    thumbnail.short_description = 'Thumbnail'

    def template_admin_url(self, obj: Meem):
        return object_url(MemeTemplate, obj.template_link.name, obj.template_link)
    template_admin_url.short_description = 'Template'

    def sourceimg_admin_urls(self, obj: Meem):
        html = ""
        for srcimg in obj.sourceimgs:
            html += object_url(MemeSourceImage, srcimg.name, srcimg) + "<br>"
        return mark_safe(html)
    sourceimg_admin_urls.short_description = 'Source images'

    def lookup_allowed(self, key, value):
        return True


class MemeImageAdmin(admin.ModelAdmin):
    list_display = ('accepted', 'thumbnail', '__str__', 'image_pool', 'change_date')
    list_display_links = ('thumbnail', '__str__')
    list_filter = ('accepted', 'image_pool')
    fields = ('name', 'friendly_name', 'image', 'image_pool', 'accepted', 'add_date', 'change_date', 'memes_link', 'image_file')
    readonly_fields = ('image', 'memes_link')
    search_fields = ('name', 'friendly_name')
    ordering = ('-change_date',)
    actions = ['accept', 'reject']

    def accept(self, request, queryset):
        queryset.update(accepted=True)
        for img in queryset:
            img.clean()
    accept.short_description = "Approve selected images"

    def reject(self, request, queryset):
        queryset.update(accepted=False)
        for img in queryset:
            img.clean()
    reject.short_description = "Reject selected images"

    def lookup_allowed(self, key, value):
        return True


@admin.register(MemeSourceImage)
class MemeSourceImageAdmin(MemeImageAdmin):
    inlines = [DiscordSourceImgSubmissionInline]

    def image(self, obj: MemeSourceImage):
        return ahref(obj.image_url, htmlimg(obj.image_url, mw=600, mh=400))
    image.short_description = 'Image'

    def thumbnail(self, obj: MemeSourceImage):
        return htmlimg(obj.image_url, mw=150, mh=150)
    thumbnail.short_description = 'Thumbnail'

    def memes_link(self, obj: MemeSourceImage):
        return list_url(Meem, {'source_images__contains': '%22' + obj.name + '%22'}, 'Go')
    memes_link.short_description = 'Memes using this image'


class MemeTemplateSlotInline(admin.TabularInline):
    model = MemeTemplateSlot
    extra = 0


@admin.register(MemeTemplate)
class MemeTemplateAdmin(MemeImageAdmin):
    inlines = [MemeTemplateSlotInline]

    def image(self, obj: MemeTemplate):
        return mark_safe(
            ahref(obj.image_url, htmlimg(obj.image_url, mw=600, mh=400)) + " " +
            ahref(obj.bgimage_url, htmlimg(obj.bgimage_url, mw=600, mh=400))
        )
    image.short_description = 'Image(s)'

    def thumbnail(self, obj: MemeTemplate):
        return htmlimg(obj.image_file and obj.image_url or obj.bgimage_url, mw=150, mh=150)
    thumbnail.short_description = 'Thumbnail'

    def memes_link(self, obj: MemeTemplate):
        return list_url(Meem, {'template_link__name': obj.name}, 'Go')
    memes_link.short_description = 'Memes using this template'

    def preview_url(self, obj: MemeTemplate):
        return ahref(obj.preview_url, 'Go', True)
    preview_url.short_description = 'Preview'

    def get_fields(self, request, obj=None):
        return super(MemeTemplateAdmin, self).get_fields(request, obj) + ('bg_image_file', 'bg_color', 'preview_url',)

    def get_readonly_fields(self, request, obj=None):
        return super(MemeTemplateAdmin, self).get_readonly_fields(request, obj) + ('preview_url',)


@admin.register(MemeImagePool)
class MemeImagePoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'friendly_name', 'pool_type', 'memeimagepoolownership')
    list_filter = ('memeimagepoolownership__status', 'pool_type',)
    fields = ('name', 'friendly_name', 'pool_type', 'srcimgs_admin_url', 'templates_admin_url')
    readonly_fields = ('srcimgs_admin_url', 'templates_admin_url')
    ordering = ('name',)
    inlines = [MemeImagePoolOwnershipInline]

    def srcimgs_admin_url(self, obj: MemeImagePool):
        return list_url(MemeSourceImage, {'image_pool': obj.pk}, 'Go')
    srcimgs_admin_url.short_description = 'Source images'

    def templates_admin_url(self, obj: MemeImagePool):
        return list_url(MemeTemplate, {'image_pool': obj.pk}, 'Go')
    templates_admin_url.short_description = 'Templates'


@admin.register(QueuedMemeImage)
class QueuedMemeImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_type', 'queue_id')
