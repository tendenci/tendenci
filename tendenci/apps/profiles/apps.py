from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_noop as _


def create_notice_types(sender, **kwargs):
    from tendenci.apps.notifications import models as notification
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("user_added",
                                    _("User Added"),
                                    _("A user has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("user_edited",
                                    _("User Edited"),
                                    _("A user has been edited."),
                                    verbosity=verbosity)
    notification.create_notice_type("user_deleted",
                                    _("User Deleted"),
                                    _("A user has been deleted"),
                                    verbosity=verbosity)


class ProfilesConfig(AppConfig):
    name = 'tendenci.apps.profiles'
    verbose_name = 'Profiles'

    def ready(self):
        super(ProfilesConfig, self).ready()
        post_migrate.connect(create_notice_types, sender=self)
