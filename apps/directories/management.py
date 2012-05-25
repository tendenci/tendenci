from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("directory_added", _("Directory Added"), _("A directory has been added."))
        notification.create_notice_type("directory_approved_user_notice", _("Directory Approved User Notice"), _("A directory has been approved - user notice."))
        #notification.create_notice_type("directory_edited", _("Directory Edited"), _("A directory has been edited."))
        notification.create_notice_type("directory_deleted", _("Directory Deleted"), _("A directory has been deleted"))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"