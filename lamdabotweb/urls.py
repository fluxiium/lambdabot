from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from lamdabotweb import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('discord_oauth2/', include('discord_oauth2.urls')),
    path('', include('website.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'LambdaBot administration'
