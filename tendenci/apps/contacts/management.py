from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("contact_submitted", _("Contact Form Submitted"), _("A contact form has been submitted."))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Contacts: Skipping creation of NoticeTypes as notification app not found"
