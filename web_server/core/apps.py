from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_server.core'
    verbose_name = _('accounts')

    def ready(self):
        import web_server.core.signals  # noqa
