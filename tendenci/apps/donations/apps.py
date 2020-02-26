from django.apps import AppConfig
from django.db.models.signals import post_migrate


class DonationsConfig(AppConfig):
    name = 'tendenci.apps.donations'
    verbose_name = 'Donations'

    def ready(self):
        super(DonationsConfig, self).ready()
        from tendenci.apps.donations.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
