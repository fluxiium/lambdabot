from django.contrib import admin

from memeviewer.models import Meem, FacebookMeem, TwitterMeem, DiscordMeem, ImageInContext, MemeTemplate, \
    MemeTemplateSlot, MemeContext, AccessToken


class FacebookInline(admin.TabularInline):
    model = FacebookMeem
    extra = 0


class TwitterInline(admin.TabularInline):
    model = TwitterMeem
    extra = 0


class DiscordInline(admin.TabularInline):
    model = DiscordMeem
    extra = 0


class MeemAdmin(admin.ModelAdmin):
    list_display = ('number', 'meme_id', 'template_link', 'context_link', 'gen_date', 'meme_url')
    ordering = ('-number', 'meme_id')
    list_display_links = ('meme_id',)
    inlines = [FacebookInline, TwitterInline, DiscordInline]
    search_fields = ('number', 'meme_id', 'context_link__name', 'context_link__short_name', 'template_link__name')

    def meme_url(self, obj):
        return '<a href="{0}" target="_blank">{1}</a>'.format(obj.get_info_url(), "Meme page")

    meme_url.allow_tags = True
    meme_url.short_description = 'Page'

admin.site.register(Meem, MeemAdmin)


class ImageInContextAdmin(admin.ModelAdmin):
    list_display = ('image_name', 'image_type', 'context_link')
    list_display_links = ('image_name',)
    search_fields = ('image_name', 'image_type', 'context_link__name', 'context_link__short_name')


admin.site.register(ImageInContext, ImageInContextAdmin)


class MemeTemplateSlotInline(admin.TabularInline):
    model = MemeTemplateSlot
    extra = 0


class MemeTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'add_date', 'preview_url')
    ordering = ('-add_date', 'name')
    search_fields = ('name',)
    inlines = [MemeTemplateSlotInline]

    def preview_url(self, obj):
        return '<a href="{0}" target="_blank">{1}</a>'.format(obj.get_preview_url(), "Preview")

    preview_url.allow_tags = True
    preview_url.short_description = 'Preview'


admin.site.register(MemeTemplate, MemeTemplateAdmin)


class MemeContextAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name')
    search_fields = ('short_name', 'name')

admin.site.register(MemeContext, MemeContextAdmin)


class AccessTokenAdmin(admin.ModelAdmin):
    pass

admin.site.register(AccessToken, AccessTokenAdmin)
