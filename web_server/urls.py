from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static


urlpatterns = [
    path('dosimagem/admin/', admin.site.urls),
    path('', include('web_server.core.urls')),
    path('api/v1/', include('web_server.api.urls')),
    path('api/v1/', include('web_server.radiosynoviorthesis.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = 'Dosimagem adminstrator'
