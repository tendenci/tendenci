from django.utils.translation import ugettext_noop as _

from tendenci.apps.notifications import models as notification
from django.db.models.signals import post_save
from tendenci.apps.events.models import Event
from tendenci.apps.contributions.signals import save_contribution


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
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


def init_signals():
    post_save.connect(save_contribution, sender=Event, weak=False)
