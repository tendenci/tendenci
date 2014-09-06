from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("job_added", _("Job Added"), _("A job has been added."))
        notification.create_notice_type("job_deleted", _("Job Deleted"), _("A job has been deleted"))
        notification.create_notice_type("job_approved_user_notice", _("Job Approved User Notice"), _("A job has been approved - user notice."))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Jobs: Skipping creation of NoticeTypes as notification app not found"
