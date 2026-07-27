from django.apps import AppConfig


class DiscourseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tendenci.apps.authentik'

    def ready(self):
        super().ready()
        from .signals import init_signals
        init_signals()

