from optparse import make_option
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Newsletter sending

    Usage:
        python manage.py send_newsletter

        example:
        python manage.py send_newsletter --newsletter 1

    """
    option_list = BaseCommand.option_list + (

        make_option(
            '--newsletter',
            action='store',
            dest='newsletter',
            default=0,
            help='Newsletter ID'),

    )

    def handle(self, *args, **options):
        from tendenci.core.emails.models import Email
        from tendenci.core.newsletters.models import Newsletter

        newsletter_id = options.get('newsletter', 0)

        if newsletter_id == 0:
            raise CommandError('Newsletter ID is required. Usage: ./manage.py send_newsletter --newsletter 1')

        newsletter = Newsletter.objects.filter(pk=int(newsletter_id))
        if newsletter.exists():
            newsletter = newsletter[0]
        else:
            newsletter = None

        if not newsletter:
            raise CommandError('You are trying to send a newsletter that does not exist.')

        recipients = newsletter.get_recipients()
        email = newsletter.email

        for recipient in recipients:
            subject = email.subject
            body = email.body

            if '[firstname]' in subject:
                subject = subject.replace('[firstname]', recipient.member.first_name)

            if '[lastname]' in subject:
                subject = subject.replace('[lastname]', recipient.member.last_name)

            if '[username]' in body:
                body = body.replace('[username]', recipient.member.username)

            if '[firstname]' in body:
                body = body.replace('[firstname]', recipient.member.first_name)

            email_to_send = Email(
                    subject=subject,
                    body=body,
                    sender=email.sender,
                    sender_display=email.sender_display,
                    reply_to=email.reply_to,
                    recipient=recipient.member.email
                    )
            email_to_send.send()

            if newsletter.send_to_email2 and recipient.member.profile.email2:
                email_to_send.recipient = recipient.member.profile.email2
                email_to_send.send()
