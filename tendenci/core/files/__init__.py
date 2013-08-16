from django.db.models.signals import post_syncdb
from django.utils.translation import ugettext_noop as _

from tendenci.apps.notifications import models as notification


def create_notice_types(app, created_models, verbosity, **kwargs):

    notification.create_notice_type(
        "file_added",
        _("File Added"),
        _("A file has been added"))

    notification.create_notice_type(
        'file_deleted',
        _('File Deleted'),
        _('A file has been deleted'))

post_syncdb.connect(create_notice_types, sender=notification)
