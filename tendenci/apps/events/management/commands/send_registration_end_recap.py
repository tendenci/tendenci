from __future__ import print_function
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Send recap email once event closes.

    An event registration is closed if the registration end date
    is less than current date.
    This command must be handled by asynchronous task queue/job
    """
    def handle(self, *args, **options):
        from tendenci.apps.base.utils import send_email_notification
        from tendenci.apps.site_settings.utils import get_setting
        from tendenci.apps.events.models import Event
        from tendenci.apps.events.utils import registration_has_recently_ended

        site_label = get_setting('site', 'global', 'sitedisplayname')
        site_url = get_setting('site', 'global', 'siteurl')
        admins = get_setting('module', 'events', 'admin_emails').split(',')
        email_list = [admin.strip() for admin in admins]

        # Query all events that are not yet marked for checking
        events = Event.objects.filter(mark_registration_ended=False)
        for event in events:
            if registration_has_recently_ended(event):
                # Calculate fees, number of participants, etc
                money_collected = event.money_collected
                money_outstanding = event.money_outstanding
                all_registrants = event.registrants()
                registrants_with_balance = event.registrants(with_balance=True)
                print('Sending email to admins for event %s.' % (event, ))
                send_email_notification(
                    'event_registration_end_recap',
                    email_list,
                    {
                        'SITE_GLOBAL_SITEDISPLAYNAME': site_label,
                        'SITE_GLOBAL_SITEURL': site_url,
                        'event': event,
                        'money_collected': money_collected,
                        'money_outstanding': money_outstanding,
                        'registrants_count': len(all_registrants),
                        'registrants_with_balance_count': len(registrants_with_balance),
                    }
                )
                print('Message sent.')

                # Mark event as ended
                event.mark_registration_ended = True
                event.save()
