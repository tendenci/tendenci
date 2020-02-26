from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_noop as _


def create_notice_types(sender, **kwargs):
    from tendenci.apps.notifications import models as notification
    notification.create_notice_type("invoice_edited",
                                    _("Invoice Edited"),
                                    _("An invoice has been edited."))

class InvoicesConfig(AppConfig):
    name = 'tendenci.apps.invoices'
    verbose_name = 'Invoices'

    def ready(self):
        super(InvoicesConfig, self).ready()
        post_migrate.connect(create_notice_types, sender=self)
