from django.apps import AppConfig
from django.db.models.signals import post_migrate


class MakePaymentsConfig(AppConfig):
    name = 'tendenci.apps.make_payments'
    verbose_name = 'Make Payments'

    def ready(self):
        super(MakePaymentsConfig, self).ready()
        from tendenci.apps.make_payments.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
