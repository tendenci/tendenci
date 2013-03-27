from datetime import datetime, timedelta
import time
import traceback

from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.template import Context, Template


class Command(BaseCommand):
    """
    Get a list of membership notices from the notice table,
    and send each notice to members who meet the criteria.

    Usage: python manage.py send_membership_notices --verbosity 1
    """

    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']

        from django.conf import settings
        from tendenci.addons.corporate_memberships.models import (
            Notice,
            CorpMembership,
            NoticeLog,
            NoticeLogRecord)
        from tendenci.core.base.utils import fieldify
        from tendenci.core.emails.models import Email
        from tendenci.core.site_settings.utils import get_setting

        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        site_contact_name = get_setting('site', 'global', 'sitecontactname')
        site_contact_email = get_setting('site', 'global', 'sitecontactemail')
        site_url = get_setting('site', 'global', 'siteurl')

        email = Email()
        email.sender = get_setting('site', 'global', 'siteemailnoreplyaddress')
        email.sender_display = site_display_name
        email.reply_to = site_contact_email

        now = datetime.now()
        nowstr = time.strftime("%d-%b-%y %I:%M %p", now.timetuple())

        def email_admins_recap(notices, total_sent):
            """Send admins recap after the notices were processed.
            """
            email.recipient = get_admin_emails()
            if email.recipient:
                template_name = "corporate_memberships/notices/email_recap.html"
                try:
                    recap_email_content = render_to_string(
                               template_name,
                               {'notices': notices,
                              'total_sent': total_sent,
                              'site_url': site_url,
                              'site_display_name': site_display_name,
                              'site_contact_name': site_contact_name,
                              'site_contact_email': site_contact_email})
                    email.body = recap_email_content
                    email.content_type = "html"
                    email.subject = '%s Corporate Membership Notices Distributed' % (
                                                    site_display_name)
                    email.send()
                except TemplateDoesNotExist:
                    pass

        def email_script_errors(err_msg):
            """Send error message to us if any.
            """
            email.recipient = get_script_support_emails()
            if email.recipient:
                email.body = '%s \n\nTime Submitted: %s\n' % (err_msg, nowstr)
                email.content_type = "text"
                email.subject = 'Error Processing Corporate Membership Notices on %s' % (
                                                            site_url)
                email.send()

        def get_script_support_emails():
            admins = getattr(settings, 'ADMINS', None)
            if admins:
                recipients_list = [admin[1] for admin in admins]
                return ','.join(recipients_list)
            return None

        def get_admin_emails():
            admin_emails = get_setting('module', 'corporate_memberships',
                                       'corporatemembershiprecipients').strip()
            if admin_emails:
                admin_emails = admin_emails.split(',')
            if not admin_emails:
                admin_emails = (get_setting('site', 'global',
                                            'admincontactemail'
                                            ).strip()).split(',')
            if admin_emails:
                admin_emails = ','.join(admin_emails)
            return admin_emails

        def process_notice(notice):
            notice.members_sent = []
            num_sent = 0
            if notice.notice_time == 'before':
                start_dt = now + timedelta(days=notice.num_days)
            else:
                start_dt = now - timedelta(days=notice.num_days)

            memberships = CorpMembership.objects.filter(
                                    status=True,
                                    status_detail__in=['active', 'expired']
                                    )
            if notice.notice_type in ['approve_join', 'disapprove_join']:
                memberships = memberships.filter(
                    approved_denied_dt__year=start_dt.year,
                    approved_denied_dt__month=start_dt.month,
                    approved_denied_dt__day=start_dt.day,
                    renewal=False)
            elif notice.notice_type in ['approve_renewal', 'disapprove_renewal']:
                memberships = memberships.filter(
                    approved_denied_dt__year=start_dt.year,
                    approved_denied_dt__month=start_dt.month,
                    approved_denied_dt__day=start_dt.day,
                    renewal=True)
            else:  # 'expire'
                memberships = memberships.filter(
                    expiration_dt__year=start_dt.year,
                    expiration_dt__month=start_dt.month,
                    expiration_dt__day=start_dt.day)

            # filter by membership type
            if notice.corporate_membership_type:
                memberships = memberships.filter(
                                corporate_membership_type=notice.corporate_membership_type)

            memberships_count = memberships.count()

            if memberships_count > 0:
                email.content_type = notice.content_type

                global_context = {'sitedisplayname': site_display_name,
                                  'sitecontactname': site_contact_name,
                                  'sitecontactemail': site_contact_email,
                                  'timesubmitted': nowstr,
                                  }

                # log notice sent
                notice_log = NoticeLog(notice=notice,
                                       num_sent=0)
                notice_log.save()
                notice.log = notice_log
                notice.err = ''

                for membership in memberships:
                    try:
                        if membership.corp_profile.email:
                            email_member(notice, membership, global_context)
                            if memberships_count <= 50:
                                notice.members_sent.append(membership)
                            num_sent += 1

                            # log record
                            notice_log_record = NoticeLogRecord(
                                                    notice_log=notice_log,
                                                    corp_membership=membership)
                            notice_log_record.save()
                    except:
                        # catch the exception and email
                        notice.err += traceback.format_exc()
                        print traceback.format_exc()

                if num_sent > 0:
                    notice_log.num_sent = num_sent
                    notice_log.save()

            return num_sent

        def email_member(notice, membership, global_context):
            corp_profile = membership.corp_profile

            body = notice.email_content
            context = membership.get_field_items()
            context['membership'] = membership
            context.update(global_context)

            if membership.expiration_dt:
                body = body.replace("[expirationdatetime]",
                                    time.strftime(
                                      "%d-%b-%y %I:%M %p",
                                      membership.expiration_dt.timetuple()))
            else:
                body = body.replace("[expirationdatetime]", '')

            context.update({'corporatemembershiptypeid':
                                str(membership.corporate_membership_type.id),
                            'corporatemembershiptype': membership.corporate_membership_type.name,
                            })

            body = fieldify(body)

            body = '%s <br /><br />%s' % (body, get_footer())

            context = Context(context)
            template = Template(body)
            body = template.render(context)

            email.recipient = corp_profile.email
            email.subject = notice.subject.replace('(name)',
                                                   corp_profile.name)
            email.body = body
            if notice.sender:
                email.sender = notice.sender
                email.reply_to = notice.sender
            if notice.sender_display:
                email.sender_display = notice.sender_display

            email.send()
            if verbosity > 1:
                print 'To ', email.recipient, email.subject

        def get_footer():
            return """
                    This e-mail was generated by Tendenci&reg; Software -
                    a web based membership management software solution
                    www.tendenci.com developed by Schipul - The Web
                    Marketing Company
                    """

        exception_str = ""

        notices = Notice.objects.filter(status=True, status_detail='active'
                                    ).exclude(notice_time='attimeof')

        if notices:
            if verbosity > 1:
                print "Start sending out notices to members:"
            total_notices = 0
            total_sent = 0
            for notice in notices:
                total_notices += 1
                total_sent += process_notice(notice)
                if hasattr(notice, 'err'):
                    exception_str += notice.err

            if total_sent > 0:
                processed_notices = [notice for notice in notices if hasattr(
                                        notice, 'log'
                                        ) and notice.log.num_sent > 0]
                email_admins_recap(processed_notices, total_sent)

            # if there is any error, notify us
            if exception_str:
                email_script_errors(exception_str)

            if verbosity > 1:
                print 'Total notice processed: %d' % (total_notices)
                print 'Total email sent: %d' % (total_sent)
                print "Done"
        else:
            if verbosity > 1:
                print "No notices on the site."

