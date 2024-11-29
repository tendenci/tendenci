from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Check and notify the members who have to come to the next conferences in order to maintain the active status. 
         - Members who have attended 2 of 4 or 1 of 3 of the most recent conferences.
         (with a certain event type).
         (If you have attended 2 for the last 4, you have to come to the next one.
         If you have attended 1 for the last 3, you have to come to the next one.)
         Exclude new members.
         
         The goal is to have members to attend  at least 3 conferences in the 5 year period. 
         Notify them if they have the potential to miss the next one.
    
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
        from datetime import datetime, timedelta
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

        # get events with this event type
        events = Event.objects.filter(type_id=event_type_id,
                                         start_dt__lt=datetime.now(),
                                         ).order_by('-start_dt')
        event_ids_last_4 = events.values_list('id', flat=True)[:4] # latest 4 events
        event_ids_last_3 = events.values_list('id', flat=True)[:3] # latest 3 events
        
        # membership type id to exclude
        exclude_m_type_id = options.get('exclude_m_type_id', None)
        if exclude_m_type_id:
            exclude_m_type_id = int(exclude_m_type_id)
        # Active members.
        memberships = MembershipDefault.objects.filter(
                        status_detail='active',
                        status=True)
        if exclude_m_type_id:
            memberships = memberships.exclude(membership_type_id=exclude_m_type_id)
        memberships = memberships.order_by('user__last_name')

        total_sent = 0
        
        site_label = get_setting('site', 'global', 'sitedisplayname')
        site_url = get_setting('site', 'global', 'siteurl')
        reply_to = get_setting('site', 'global', 'admincontactemail').split(',')[0]
        
        def is_requirements_met(membership, years_period):
            # years_period - either 4 or 3
            if years_period == 4:
                # if attended exact 2 in the 4 years perid and the first attendance date is 3 years ago
                return Registrant.objects.filter(
                    registration__event_id__in=list(event_ids_last_4),
                    user=membership.user,
                    cancel_dt__isnull=True).count() == 2 and \
                Registrant.objects.filter(
                    registration__event_id__in=list(events.filter(
                        start_dt__lt=(datetime.now() - timedelta(days=3*365))
                        ).values_list('id', flat=True)),
                    user=membership.user,
                    cancel_dt__isnull=True).exists()
            if years_period == 3:
                # if attended exact 1 in the 3 years perid and the first attendance date is 2 years ago
                return Registrant.objects.filter(
                    registration__event_id__in=list(event_ids_last_3),
                    user=membership.user,
                    cancel_dt__isnull=True).count() == 1 and \
                Registrant.objects.filter(
                    registration__event_id__in=list(events.filter(
                        start_dt__lt=(datetime.now() - timedelta(days=2*365))
                        ).values_list('id', flat=True)),
                    user=membership.user,
                    cancel_dt__isnull=True).exists()
            return False

        members_list = []   
        for membership in memberships:
            # 2 of 4 or 1 or 3
            if is_requirements_met(membership, 4) or is_requirements_met(membership, 3):
                # send notification email to user
                user_email = membership.user.email
                print(membership.user.first_name, membership.user.last_name, user_email)

                if not validate_email(user_email) or Email.is_blocked(user_email):
                    print(f'Skipping ... not valid email "{user_email}"')
                    if total_sent < 30:
                        members_list.append(user_email + ' ... invalid email or email blocked')
                    continue

                if total_sent < 30:
                    members_list.append(user_email)

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
            if total_sent >= 30:
                members_list.append('more ...')
            # send recap to admin
            email = Email()
            email.recipient = reply_to
            email.subject = f'{site_label} Conference Attendance Notice Distributed'
            if total_sent == 1:
                m_txt = '1 member'
            else:
                m_txt = f'{total_sent} members'
            email.body = f"""The Conference Attendance Notice has been distributed to {m_txt}.<br />"""
            email.body += '<br />'.join(members_list)
            email.body += f"""<br /><br />Thanks!<br /><br />{site_label}"""
            email.send()

        print('Done')
