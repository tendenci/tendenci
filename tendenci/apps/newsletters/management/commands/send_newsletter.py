
from builtins import str
import datetime
import traceback
import re
from logging import getLogger
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.template.loader import render_to_string
from django.urls import reverse


class Command(BaseCommand):
    """
    Newsletter sending

    Usage:
        python manage.py send_newsletter

        example:
        python manage.py send_newsletter 1

    """
    def add_arguments(self, parser):
        parser.add_argument('newsletter_id', type=int)

    def send_newsletter(self, newsletter_id, **kwargs):
        from tendenci.apps.emails.models import Email
        from tendenci.apps.newsletters.models import Newsletter, NewsletterRecurringData
        from tendenci.apps.site_settings.utils import get_setting
        from tendenci.apps.base.utils import validate_email

        from tendenci.apps.newsletters.utils import get_newsletter_connection

        connection = get_newsletter_connection()
        if not connection:
            print('Exiting..Please set up your newsletter email provider before proceeding.')
            return

        print("Started sending newsletter...")

        if newsletter_id == 0:
            raise CommandError('Newsletter ID is required. Usage: ./manage.py send_newsletter <newsletter_id>')

        newsletter = Newsletter.objects.filter(pk=int(newsletter_id))
        if newsletter.exists():
            newsletter = newsletter[0]
        else:
            newsletter = None

        if not newsletter:
            raise CommandError('You are trying to send a newsletter that does not exist.')
        
        # validate sender
        if not validate_email(newsletter.email.sender):
            raise CommandError('"{}" is not a valid sender email address.'.format(newsletter.email.sender))

        if newsletter.send_status == 'queued':
            newsletter.send_status = 'sending'

        elif newsletter.send_status == 'sent':
            newsletter.send_status = 'resending'

        elif newsletter.send_status == 'resent':
            newsletter.send_status == 'resending'

        newsletter.save()

        if newsletter.schedule:
            # save start_dt and status for the recurring
            nr_data = NewsletterRecurringData(
                        newsletter=newsletter,
                        start_dt=datetime.datetime.now(),
                        send_status=newsletter.send_status)
            nr_data.save()
            newsletter.nr_data = nr_data

        recipients = newsletter.get_recipients()
        email = newsletter.email
        # replace relative to absolute urls
        self.site_url = get_setting('site', 'global', 'siteurl')
        email.body = email.body.replace("src=\"/", "src=\"%s/" % self.site_url)
        email.body = email.body.replace("href=\"/", "href=\"%s/" % self.site_url)

        if newsletter.group and newsletter.group.membership_types.all().exists():
            membership_type = newsletter.group.membership_types.all()[0]
        else:
            membership_type = None

        counter = 0
        for recipient in recipients:
            if hasattr(recipient.member, 'profile'):
                profile = recipient.member.profile
            else:
                profile = None

            # Skip if Don't Send Email is on
            if newsletter.enforce_direct_mail_flag:
                if profile and not profile.direct_mail:
                    continue

            # skip if not a valid email address
            if not validate_email(recipient.member.email):
                continue

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
                #body = body.replace('[unsubscribe_url]', recipient.noninteractive_unsubscribe_url)
                # The unsubscribe_url link should be something like <a href="[unsubscribe_url]">Unsubscribe</a>.
                # But it can be messed up sometimes. Let's prevent that from happening.
                p = r'(href=\")([^\"]*)(\[unsubscribe_url\])(\")'
                body = re.sub(p, r'\1' + recipient.noninteractive_unsubscribe_url + r'\4', body)

            if '[browser_view_url]' in body:
                body = body.replace('[browser_view_url]', newsletter.get_browser_view_url())

            if membership_type:
                [membership] = recipient.member.membershipdefault_set.exclude(
                        status_detail='archive').order_by('-create_dt')[:1] or [None]
                if membership:
                    # do find and replace
                    urls_dict = membership.get_common_urls(site_url=self.site_url)
                    for key in urls_dict.keys():
                        body = body.replace('[%s]' % key, urls_dict[key])

            email_to_send = Email(
                    subject=subject,
                    body=body,
                    sender=email.sender,
                    sender_display=email.sender_display,
                    reply_to=email.reply_to,
                    recipient=recipient.member.email
                    )
            print(u"Sending to {}".format(str(recipient.member.email)))
            email_to_send.send(connection=connection)
            counter += 1
            print(u"Newsletter sent to {}".format(str(recipient.member.email)))

            if newsletter.send_to_email2 and hasattr(recipient.member, 'profile') \
                and validate_email(recipient.member.profile.email2):
                email_to_send.recipient = recipient.member.profile.email2
                email_to_send.send(connection=connection)
                counter += 1
                print(u"Newsletter sent to {}".format(str(recipient.member.profile.email2)))

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
        if newsletter.schedule and newsletter.nr_data:
            # save the finish_dt and email_sent_count for the recurring
            newsletter.nr_data.finish_dt = datetime.datetime.now()
            newsletter.nr_data.email_sent_count = newsletter.email_sent_count
            newsletter.nr_data.send_status = newsletter.send_status
            newsletter.nr_data.save()

        print("Successfully sent %s newsletter emails." % counter)

        print("Sending confirmation message to creator...")
        # send confirmation email
        subject = "Newsletter Submission Recap for %s" % newsletter.email.subject
        detail_url = get_setting('site', 'global', 'siteurl') + newsletter.get_absolute_url()
        params = {'first_name': newsletter.email.creator.first_name,
                    'subject': newsletter.email.subject,
                    'count': counter,
                    'detail_url': detail_url}

        body = render_to_string(
                template_name='newsletters/newsletter_sent_email_body.html', context=params)

        email = Email(
            recipient=newsletter.email.sender,
            subject=subject,
            body=body)

        email.send(connection=connection)

        print("Confirmation email sent.")

        # add cache clear to resolve issue
        # TODO: cache clear only to specifies
        cache.clear()
        print('Cache cleared!')

    def handle(self, *args, **options):
        from tendenci.apps.site_settings.utils import get_setting
        logger = getLogger('send_newsletter')

        newsletter_id = options['newsletter_id']

        try:
            self.send_newsletter(newsletter_id)
        except:
            print(traceback.format_exc())
            newsletter_url = '%s%s' % (get_setting('site', 'global', 'siteurl'),
                                        reverse('newsletter.detail.view', kwargs={'pk': newsletter_id}))
            logger.error('Error sending newsletter %s...\n\n%s' % (newsletter_url, traceback.format_exc()))
