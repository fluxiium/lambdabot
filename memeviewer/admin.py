from django.contrib import admin

from memeviewer.models import Meem, FacebookMeem, TwitterMeem, DiscordMeem


class MeemAdmin(admin.ModelAdmin):
    pass


class FacebookMeemAdmin(admin.ModelAdmin):
    pass


class TwitterMeemAdmin(admin.ModelAdmin):
    pass


class DiscordMeemAdmin(admin.ModelAdmin):
    pass


admin.site.register(Meem, MeemAdmin)
admin.site.register(FacebookMeem, FacebookMeemAdmin)
admin.site.register(TwitterMeem, TwitterMeemAdmin)
admin.site.register(DiscordMeem, DiscordMeemAdmin)
