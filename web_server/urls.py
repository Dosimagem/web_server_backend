from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('dosimagem/admin/', admin.site.urls),
    path('', include('web_server.core.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))


admin.site.site_header = 'Dosimagem adminstrator'
