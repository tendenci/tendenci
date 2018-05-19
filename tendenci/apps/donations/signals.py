from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_migrate

from tendenci.apps.notifications import models as notification

def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("donation_added",
                                    _("Donation Added"),
                                    _("A donation has been added."),
                                    verbosity=verbosity)


def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.donations.models import Donation
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Donation, weak=False)
