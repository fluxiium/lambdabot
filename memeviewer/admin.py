from django.contrib import admin
from django.utils.safestring import mark_safe

from discordbot.models import DiscordMeem
from facebookbot.models import FacebookMeem
from memeviewer.models import Meem, ImageInContext, MemeTemplate, \
    MemeTemplateSlot, MemeContext, AccessToken, MemeSourceImageOverride, Setting
from twitterbot.models import TwitterMeem


class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    ordering = ('key',)
    search_fields = ('key', 'value')

admin.site.register(Setting, SettingAdmin)


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
    search_fields = ('number', 'meme_id', 'context_link__short_name', 'template_link__name', 'sourceimgs')

    readonly_fields = ['image', 'meme_url']
    fields = tuple([f.name for f in Meem._meta.fields + Meem._meta.many_to_many] + readonly_fields)
    readonly_fields = tuple(readonly_fields)

    def meme_url(self, obj):
        return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(obj.get_info_url(), "Meme page"))

    meme_url.short_description = 'Page'

    def image(self, obj):
        return mark_safe('<img src="{}" width="350">'.format(obj.get_url()))

    image.short_description = 'Image'

admin.site.register(Meem, MeemAdmin)


class ImageInContextAdmin(admin.ModelAdmin):
    list_display = ('image_name', 'image_type', 'context_link')
    list_display_links = ('image_name',)
    search_fields = ('image_name', 'image_type', 'context_link__short_name')

admin.site.register(ImageInContext, ImageInContextAdmin)


class MemeSourceImageOverrideAdmin(admin.ModelAdmin):
    list_display = ('name', 'add_date', 'disabled')
    ordering = ('name', '-add_date')

    readonly_fields = ['image']
    fields = tuple([f.name for f in MemeSourceImageOverride._meta.fields + MemeSourceImageOverride._meta.many_to_many] + readonly_fields)
    readonly_fields = tuple(readonly_fields)

    def image(self, obj):
        return mark_safe('<img src="{}" width="350">'.format(obj.get_image_url()))

    image.short_description = 'Image'

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(MemeSourceImageOverrideAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= MemeSourceImageOverride.search(search_term)
        return queryset, use_distinct

admin.site.register(MemeSourceImageOverride, MemeSourceImageOverrideAdmin)


class MemeTemplateSlotInline(admin.TabularInline):
    model = MemeTemplateSlot
    extra = 0


class MemeTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'add_date', 'contexts_string', 'disabled', 'preview_url')
    ordering = ('-add_date', 'name')
    inlines = [MemeTemplateSlotInline]

    readonly_fields = ['image', 'preview_url']
    fields = tuple([f.name for f in MemeTemplate._meta.fields + MemeTemplate._meta.many_to_many] + readonly_fields)
    readonly_fields = tuple(readonly_fields)

    def preview_url(self, obj):
        return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(obj.get_preview_url(), "Preview"))

    preview_url.short_description = 'Preview'

    def image(self, obj):
        return mark_safe('<img src="{}" width="350">'.format(obj.get_image_url()))

    image.short_description = 'Image'

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(MemeTemplateAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= MemeTemplate.search(search_term)
        return queryset, use_distinct

admin.site.register(MemeTemplate, MemeTemplateAdmin)


class MemeContextAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'reset_url')
    search_fields = ('short_name', 'name')
    ordering = ('name',)

    def reset_url(self, obj):
        return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(obj.get_reset_url(), "Reset"))

    reset_url.short_description = 'Reset queue'

admin.site.register(MemeContext, MemeContextAdmin)


class AccessTokenAdmin(admin.ModelAdmin):
    pass

admin.site.register(AccessToken, AccessTokenAdmin)
