from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Check and notify the members who have the low event attendance rate
         - NOT attended at least 3 out of 5 of past conferences
         (with a certain event type).
    
    Usage:
    
        ./manage.py members_with_low_attendance_rate --event_type_id=<event-type-id> --verbosity=2
    """
    def add_arguments(self, parser):
        parser.add_argument('--event_type_id',
            dest='event_type_id',
            default=None,
            help='The id of the event type to be checked')

    def handle(self, *args, **options):
        from tendenci.apps.base.utils import validate_email
        from tendenci.apps.emails.models import Email
        from tendenci.apps.profiles.models import Profile
        from tendenci.apps.site_settings.utils import get_setting
        from tendenci.apps.notifications import models as notification
        from tendenci.apps.events.models import Type as EventType, Registrant, Event

        verbosity = options['verbosity']
        event_type_id = options['event_type_id']
        if not EventType.objects.filter(id=event_type_id).exists():
            print('Event type with id ', event_type_id, "doesn't exist. Exiting")
            return

        # get latest 5 events with this event type
        event_ids = Event.objects.filter(type_id=event_type_id
                                         ).values_list('id', flat=True
                                                       )[:5]
        # members only
        for profile in Profile.objects.exclude(member_number=''
                                ).exclude(member_number__isnull=True):
            if Registrant.objects.filter(
                        registration__event_id__in=event_ids,
                        user=profile.user,
                        cancel_dt__isnull=True).count() < 3:
                # send notification email to user
                user_email = profile.user.email
                if not validate_email(user_email) or Email.is_blocked(user_email):
                    print(f'Skipping ... not valid email "{user_email}"')
                    continue

                site_label = get_setting('site', 'global', 'sitedisplayname')
                site_url = get_setting('site', 'global', 'siteurl')
                reply_to = get_setting('site', 'global', 'allnoticerecipients').split(',')[0]
                notification.send_emails(
                    [user_email],  # recipient(s)
                    'event_low_attendance_rate_notice',  # template
                    {
                        'SITE_GLOBAL_SITEDISPLAYNAME': site_label,
                        'SITE_GLOBAL_SITEURL': site_url,
                        'site_label': site_label,
                        'site_url': site_url,
                        'profile': profile,
                        'reply_to': reply_to,
                    },
                    True,  # notice saved in db
                ) 

        print('Done')
