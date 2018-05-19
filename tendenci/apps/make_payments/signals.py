from django.utils.translation import ugettext_noop as _
from tendenci.apps.notifications import models as notification


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("make_payment_added",
                                    _("Make Payment Added"),
                                    _("A payment has been made."),
                                    verbosity=verbosity)


def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.make_payments.models import MakePayment
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=MakePayment, weak=False)
