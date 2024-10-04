from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Check and notify the members who have the low event attendance
         - NOT attended at least 3 out of 5 of past conferences
         (with a certain event type).
    
    Usage:
    
        ./manage.py email_members_with_low_attendance --event_type_id=<event-type-id> --exclude_m_type_id --verbosity=2
        
        Example:
        ./manage.py email_members_with_low_attendance --event_type_id=1 --exclude_m_type_id=4
    """
    def add_arguments(self, parser):
        parser.add_argument('--event_type_id',
            dest='event_type_id',
            default=None,
            help='The id of the event type to be checked')
        parser.add_argument('--exclude_m_type_id',
            dest='exclude_m_type_id',
            default=None,
            help='The id of the membership type to exclude')

    def handle(self, *args, **options):
        from tendenci.apps.base.utils import validate_email
        from tendenci.apps.emails.models import Email
        from tendenci.apps.memberships.models import MembershipDefault
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
                                         ).order_by('-start_dt'
                                        ).values_list('id', flat=True)[:5]
        exclude_m_type_id = options.get('exclude_m_type_id', None)
        if exclude_m_type_id:
            exclude_m_type_id = int(exclude_m_type_id)
        # members only
        memberships = MembershipDefault.objects.filter(status_detail='active', status=True)
        if exclude_m_type_id:
            memberships = memberships.exclude(membership_type_id=exclude_m_type_id)
        memberships = memberships.order_by('user__last_name')
        total_sent = 0
        
        site_label = get_setting('site', 'global', 'sitedisplayname')
        site_url = get_setting('site', 'global', 'siteurl')
        reply_to = get_setting('site', 'global', 'admincontactemail').split(',')[0]
        
        for membership in memberships:
            if Registrant.objects.filter(
                        registration__event_id__in=list(event_ids),
                        user=membership.user,
                        cancel_dt__isnull=True).count() < 3:
                # send notification email to user
                user_email = membership.user.email
                print(membership.user.first_name, membership.user.last_name, user_email)

                if not validate_email(user_email) or Email.is_blocked(user_email):
                    print(f'Skipping ... not valid email "{user_email}"')
                    continue
        
                notification.send_emails(
                    [user_email],  # recipient(s)
                    'event_low_attendance_notice',  # template
                    {
                        'SITE_GLOBAL_SITEDISPLAYNAME': site_label,
                        'SITE_GLOBAL_SITEURL': site_url,
                        'site_label': site_label,
                        'site_url': site_url,
                        'membership': membership,
                        'reply_to': reply_to,
                    },
                    True,  # notice saved in db
                )
                total_sent += 1 

        if total_sent > 0 and reply_to:
            # send recap to admin
            email = Email()
            email.recipient = reply_to
            email.subject = f'{site_label} Event Low Attendance Notice Distributed'
            if total_sent == 1:
                m_txt = '1 member'
            else:
                m_txt = f'{total_sent} members'
            email.body = f"""The Low Attendance Notice has been distributed to {m_txt}.
                        <br /><br />Thanks!<br /><br />{site_label}"""
            email.send()

        print('Done')
