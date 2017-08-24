from django.contrib import admin

from memeviewer.models import Meem


class MeemAdmin(admin.ModelAdmin):
    pass


admin.site.register(Meem, MeemAdmin)
