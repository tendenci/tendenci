from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


class Command(BaseCommand):
    """
    Newsletter sending

    Usage:
        python manage.py send_newsletter

        example:
        python manage.py send_newsletter 1

    """
    def handle(self, *args, **options):
        import datetime
        from tendenci.core.emails.models import Email
        from tendenci.core.newsletters.models import Newsletter
        from tendenci.core.site_settings.utils import get_setting

        from tendenci.core.newsletters.utils import get_newsletter_connection

        connection = get_newsletter_connection()
        if not connection:
            print('Exiting..Please set up your newsletter email provider before proceeding.')
            return


        print "Started sending newsletter..."

        newsletter_id = int(args[0])

        if newsletter_id == 0:
            raise CommandError('Newsletter ID is required. Usage: ./manage.py send_newsletter <newsletter_id>')

        newsletter = Newsletter.objects.filter(pk=int(newsletter_id))
        if newsletter.exists():
            newsletter = newsletter[0]
        else:
            newsletter = None

        if not newsletter:
            raise CommandError('You are trying to send a newsletter that does not exist.')

        if newsletter.send_status == 'queued':
            newsletter.send_status = 'sending'

        elif newsletter.send_status == 'sent':
            newsletter.send_status = 'resending'

        elif newsletter.send_status == 'resent':
            newsletter.send_status == 'resending'

        newsletter.save()

        recipients = newsletter.get_recipients()
        email = newsletter.email
        # replace relative to absolute urls
        self.site_url = get_setting('site', 'global', 'siteurl')
        email.body = email.body.replace("src=\"/", "src=\"%s/" % self.site_url)
        email.body = email.body.replace("href=\"/", "href=\"%s/" % self.site_url)


        counter = 0
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

            if '[unsubscribe_url]' in body:
                body = body.replace('[unsubscribe_url]', recipient.noninteractive_unsubscribe_url)

            if '[browser_view_url]' in body:
                body = body.replace('[browser_view_url]', newsletter.get_browser_view_url())

            email_to_send = Email(
                    subject=subject,
                    body=body,
                    sender=email.sender,
                    sender_display=email.sender_display,
                    reply_to=email.reply_to,
                    recipient=recipient.member.email
                    )
            email_to_send.send(connection=connection)
            counter += 1
            print "Newsletter sent to %s" % recipient.member.email

            if newsletter.send_to_email2 and hasattr(recipient.member, 'profile') \
                    and recipient.member.profile.email2:
                email_to_send.recipient = recipient.member.profile.email2
                email_to_send.send(connection=connection)
                counter += 1
                print "Newsletter sent to %s" % recipient.member.profile.email2

        if newsletter.send_status == 'sending':
            newsletter.send_status = 'sent'
            newsletter.date_email_sent = datetime.datetime.now()

        elif newsletter.send_status == 'resending':
            newsletter.send_status = 'resent'
            newsletter.date_last_resent = datetime.datetime.now()
            if not newsletter.resend_count:
                newsletter.resend_count = 0
            newsletter.resend_count += 1

        newsletter.email_sent_count = counter

        newsletter.save()

        print "Successfully sent %s newsletter emails." % counter

        print "Sending confirmation message to creator..."
        # send confirmation email
        subject = "Newsletter Submission Recap for %s" % newsletter.email.subject
        detail_url = self.site_url + \
                reverse('newsletter.detail.view', kwargs={'pk': newsletter.pk})
        params = {'first_name': newsletter.email.creator.first_name,
                    'subject': newsletter.email.subject,
                    'count': counter,
                    'detail_url': detail_url}

        body = render_to_string(
                'newsletters/newsletter_sent_email_body.html', params)

        email = Email(
            recipient=newsletter.email.sender,
            subject=subject,
            body=body)

        email.send(connection=connection)

        print "Confirmation email sent."

        # add cache clear to resolve issue
        # TODO: cache clear only to specifies
        cache.clear()
        print 'Cache cleared!'
