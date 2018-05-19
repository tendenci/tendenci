from django.utils.translation import ugettext_noop as _
from tendenci.apps.notifications import models as notification


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("help_file_requested",
                                    _("Help File Requested"),
                                    _("A help file has been requested."),
                                    verbosity=verbosity)


def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.help_files.models import HelpFile
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=HelpFile, weak=False)
