from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_noop as _


def create_notice_types(sender, **kwargs):
    from tendenci.apps.notifications import models as notification
    verbosity = kwargs.get('verbosity', 2)
    
    notification.create_notice_type("page_added",
                                    _("Page Added"),
                                    _("A page has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("page_edited",
                                    _("Page Edited"),
                                    _("A page has been edited."),
                                    verbosity=verbosity)
    notification.create_notice_type("page_deleted",
                                    _("Page Deleted"),
                                    _("A page has been deleted"),
                                    verbosity=verbosity)



class PagesConfig(AppConfig):
    name = 'tendenci.apps.pages'
    verbose_name = 'Pages'

    def ready(self):
        super(PagesConfig, self).ready()
        post_migrate.connect(create_notice_types, sender=self)
