from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("resume_added", _("Resume Added"), _("A resume has been added."))
        notification.create_notice_type("resume_deleted", _("Resume Deleted"), _("A resume has been deleted"))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Resumes: Skipping creation of NoticeTypes as notification app not found"
