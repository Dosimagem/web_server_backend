from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SignatureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_server.signature'
    verbose_name = _('signature')
