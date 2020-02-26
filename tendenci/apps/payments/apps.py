from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_noop as _


def create_notice_types(sender, **kwargs):
    from tendenci.apps.notifications import models as notification
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("payment_added",
                                    _("Payment Generated"),
                                    _("A payment has been generated."),
                                    verbosity=verbosity)


class PaymentsConfig(AppConfig):
    name = 'tendenci.apps.payments'
    verbose_name = 'Payments'

    def ready(self):
        super(PaymentsConfig, self).ready()
        post_migrate.connect(create_notice_types, sender=self)
