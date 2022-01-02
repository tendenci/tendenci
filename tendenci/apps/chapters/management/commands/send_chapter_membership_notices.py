
from datetime import datetime, timedelta
import time
import traceback
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.template.loader import render_to_string
from django.template import engines, TemplateDoesNotExist


class Command(BaseCommand):
    """
    Get a list of chapter membership notices from the notice table,
    and send each notice to chapter members who meet the criteria.

    Usage: python manage.py send_chapter_membership_notices --verbosity 2
    """

    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = int(options['verbosity'])

        from ...models import Notice
        from tendenci.apps.notifications import models as notification
        from tendenci.apps.site_settings.utils import get_setting

        def email_admins_recap(notices, total_sent):
            """Send admins recap after the notices were processed.
            """
            recap_recipient = get_admin_emails()
            if recap_recipient:
                template_name = "chapters/notices/admin_email_recap.html"
                site_display_name = get_setting('site', 'global', 'sitedisplayname')
                site_contact_name = get_setting('site', 'global', 'sitecontactname')
                site_contact_email = get_setting('site', 'global', 'sitecontactemail')
                site_url = get_setting('site', 'global', 'siteurl')
        
                email_context = {
                    'sender_display':site_display_name,
                    'reply_to':site_contact_email}
                recap_email_content = render_to_string(
                           template_name=template_name,
                           context={'notices': notices,
                          'total_sent': total_sent,
                          'site_url': site_url,
                          'site_display_name': site_display_name,
                          'site_contact_name': site_contact_name,
                          'site_contact_email': site_contact_email})
                recap_subject = f'{site_display_name} Chapter Membership Notices Distributed'
                email_context.update({
                    'subject':recap_subject,
                    'content': recap_email_content,
                    'content_type':"html"})

                notification.send_emails(recap_recipient, 'chapter_membership_notice_email',
                                         email_context)

        def get_admin_emails():
            admin_emails = get_setting('module', 'chapters',
                                       'chapterrecipients').strip()
            if admin_emails:
                admin_emails = admin_emails.split(',')
            if not admin_emails:
                admin_emails = (get_setting('site', 'global',
                                            'admincontactemail'
                                            ).strip()).split(',')
            return admin_emails


        notices = Notice.objects.filter(status=True, status_detail='active'
                                    ).exclude(notice_time='attimeof')

        if notices:
            if verbosity > 1:
                print("Start sending out notices to chapter members:")
            total_notices = 0
            total_sent = 0
            for notice in notices:
                total_notices += 1
                total_sent += notice.process_notice(verbosity=verbosity)

            if total_sent > 0:
                processed_notices = [notice for notice in notices if hasattr(
                                        notice, 'log'
                                        ) and notice.log.num_sent > 0]
                email_admins_recap(processed_notices, total_sent)

            if verbosity > 1:
                print('Total notice processed: %d' % (total_notices))
                print('Total email sent: %d' % (total_sent))
                print("Done")
        else:
            if verbosity > 1:
                print("No notices on the site.")
