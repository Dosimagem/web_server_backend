from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from web_server.core.views.index import index
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)


def trigger_error(request):
    return 1 / 0


urlpatterns = [
    path('favicon.ico', favicon_view),
    #
    path('dosimagem/admin/', admin.site.urls),
    path('', index),
    # API
    path('api/v1/', include('web_server.core.urls')),
    path('api/v1/', include('web_server.service.urls')),
    path('api/v1/', include('web_server.radiosynoviorthesis.urls')),
    path('api/v1/', include('web_server.signature.urls')),
    path('api/v1/', include('web_server.budget.urls')),
    path('api/v1/', include('web_server.notification.urls')),
    # For teste sentry
    path('sentry-debug/', trigger_error),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = 'Dosimagem administrator'
