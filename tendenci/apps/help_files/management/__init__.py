from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("help_file_requested", _("Help File Requested"), _("A help file has been requested."))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Help Files: Skipping creation of NoticeTypes as notification app not found"
