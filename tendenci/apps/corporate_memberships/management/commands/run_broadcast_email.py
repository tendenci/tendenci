
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string


class Command(BaseCommand):
    """
    Run broadcast emails for corp.

    Usage:
        python manage.py run_broadcast_email <id>

        example:
        python manage.py run_broadcast_email 1

    """
    def add_arguments(self, parser):
        parser.add_argument('id', type=int)

    def handle(self, *args, **options):
        import datetime
        from django.contrib.auth.models import User
        from tendenci.apps.newsletters.utils import get_newsletter_connection
        from tendenci.apps.emails.models import Email
        from tendenci.apps.corporate_memberships.models import CorpMembership, CorpProfile, BroadcastEmail

        # Validating data that are passed in
        bce_id = options.get('id', None)
        if not bce_id:
            msg = 'Please pass id of BroadcastEmail'
            raise CommandError(msg)
        
        try:
            bce = BroadcastEmail.objects.get(pk=bce_id)
        except BroadcastEmail.DoesNotExist:
            msg = f'BroadcastEmail table does not have id={bce_id}'
            raise CommandError(msg)

        email_id = bce.params_dict['email_id']
        [email] = Email.objects.filter(id=email_id)[:1] or [None]
        if not email:
            raise CommandError('email does not exist.')

        corp_member_ids = [int(id) for id in bce.params_dict['corp_member_ids'].split(',')]
        corp_members = CorpMembership.objects.filter(id__in=corp_member_ids)[:1] or [None]
        if not corp_members:
            raise CommandError('No corp members passed.')

        print("Sending email to corporate members ...")

        total_sent = 0
        connection = get_newsletter_connection()

        for corp_member in corp_members:
            corp_profile = corp_member.corp_profile
            reps = corp_member.corp_profile.reps.filter(is_member_rep=True)
            corp_profile.num_reps = len(reps)
            for rep in reps:
                email.recipient = rep.user.email
                if email.recipient:
                    email.send(connection=connection)
                    total_sent += 1
        
        bce.status = "completed"
        bce.total_sent = total_sent
        bce.finish_dt = datetime.datetime.now()
        bce.save()

        # Sending summary to the creator
        summary = f'Total emails sent to {total_sent}\n\n'
        summary += 'Email Sent Appears Below in Raw Format:\n'
        summary += email.body
        email.subject = f'SUMMARY: {email.subject}'
        email.body = summary
        email.recipient = bce.creator.email
        email.send()

        print("Done!")
