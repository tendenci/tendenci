from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("article_added", _("Article Added"), _("An article has been added."))
        #notification.create_notice_type("article_edited", _("Article Edited"), _("An article has been edited."))
        notification.create_notice_type("article_deleted", _("Article Deleted"), _("An article has been deleted"))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print _("Articles - Skipping creation of NoticeTypes as notification app not found")
