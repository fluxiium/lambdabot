from django.contrib import admin

from memeviewer.models import Meem, FacebookMeem, TwitterMeem


class MeemAdmin(admin.ModelAdmin):
    pass


class FacebookMeemAdmin(admin.ModelAdmin):
    pass


class TwitterMeemAdmin(admin.ModelAdmin):
    pass


admin.site.register(Meem, MeemAdmin)
admin.site.register(FacebookMeem, FacebookMeemAdmin)
admin.site.register(TwitterMeem, TwitterMeemAdmin)
