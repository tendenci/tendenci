from django.apps import AppConfig
from django.db.models.signals import post_migrate


class EventsConfig(AppConfig):
    name = 'tendenci.apps.events'
    verbose_name = 'Events'

    def ready(self):
        super(EventsConfig, self).ready()
        from tendenci.apps.events.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
