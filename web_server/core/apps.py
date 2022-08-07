from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_server.core'

    def ready(self):
        import web_server.core.signals  # noqa
