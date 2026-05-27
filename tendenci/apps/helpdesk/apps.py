from django.apps import AppConfig

class HelpdeskConfig(AppConfig):
    name = 'tendenci.apps.helpdesk'
    verbose_name = "Helpdesk"

    def ready(self):
        super().ready()
        from tendenci.apps.helpdesk.signals import init_signals
        init_signals()
