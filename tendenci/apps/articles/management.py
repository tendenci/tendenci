from __future__ import print_function
from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_migrate

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, verbosity, **kwargs):
        notification.create_notice_type("article_added", _("Article Added"), _("An article has been added."), verbosity=verbosity)
        #notification.create_notice_type("article_edited", _("Article Edited"), _("An article has been edited."), verbosity=verbosity)
        notification.create_notice_type("article_deleted", _("Article Deleted"), _("An article has been deleted"), verbosity=verbosity)

    post_migrate.connect(create_notice_types, sender=notification)
else:
    print(_("Articles - Skipping creation of NoticeTypes as notification app not found"))
