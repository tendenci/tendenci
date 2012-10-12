from django.db.models.signals import post_syncdb
from django.conf import settings
from django.utils.translation import ugettext_noop as _

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("wp_import", _("Wordpress Blog Import"), _("A blog has been imported from wordpress."))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Failed to add type"
