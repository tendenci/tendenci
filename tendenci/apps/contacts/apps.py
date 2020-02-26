from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_noop as _


def create_notice_types(sender, **kwargs):
    from tendenci.apps.notifications import models as notification
    notification.create_notice_type("contact_submitted",
                                    _("Contact Form Submitted"),
                                    _("A contact form has been submitted."))


class ContactsConfig(AppConfig):
    name = 'tendenci.apps.contacts'
    verbose_name = 'Contacts'

    def ready(self):
        super(ContactsConfig, self).ready()
        post_migrate.connect(create_notice_types, sender=self)
