from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_noop as _

from tendenci.apps.notifications import models as notification


def create_notice_types(app, verbosity, **kwargs):
    notification.create_notice_type(
        'event_added',
        _('Event Added'),
        _('An event has been added'),
        verbosity=verbosity)

    notification.create_notice_type(
        'event_edited',
        _('Event Edited'),
        _('An event has been edited'),
        verbosity=verbosity)

    notification.create_notice_type(
        'event_deleted',
        _('Event Deleted'),
        _('An event has been deleted'),
        verbosity=verbosity)

    notification.create_notice_type(
        'event_registration_confirmation',
        _('Event Registration Confirmation'),
        _('The email you receive confirming your registration'),
        verbosity=verbosity)

    notification.create_notice_type(
        'event_registration_cancelled',
        _('Event Registration Cancelled'),
        _('Notify administrators that someone has cancelled their event registration'),
        verbosity=verbosity)

    notification.create_notice_type(
        'event_registration_end_recap',
        _('Recap of end of event registration'),
        _('Notify administrators that registration for the event has ended.'),
        verbosity=verbosity)

post_migrate.connect(create_notice_types, sender=notification)
