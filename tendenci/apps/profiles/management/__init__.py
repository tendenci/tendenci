from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

# The post_syncdb signal is not being called because
# this profile application has migration files via
# the schemamigration command.
# TODO: The profiles application must use startmigration
# command in order to continue using the post_syncdb signal
# TODO: Or we can create a migration file for this function,
# as suggested by the site.
# http://south.aeracode.org/docs/commands.html?highlight=post_syncdb#initial-data-and-post-syncdb
if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("user_added", _("User Added"), _("A user has been added."))
        notification.create_notice_type("user_edited", _("User Edited"), _("A user has been edited."))
        notification.create_notice_type("user_deleted", _("User Deleted"), _("A user has been deleted"))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Profiles: Skipping creation of NoticeTypes as notification app not found"
