from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("page_added", _("Page Added"), _("A page has been added."))
        notification.create_notice_type("page_edited", _("Page Edited"), _("A page has been edited."))
        notification.create_notice_type("page_deleted", _("Page Deleted"), _("A page has been deleted"))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Pages: Skipping creation of NoticeTypes as notification app not found"
