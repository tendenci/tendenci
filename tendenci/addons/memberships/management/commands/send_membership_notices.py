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
        from tendenci.addons.memberships.models import (Notice,
                                                        MembershipDefault,
                                                        NoticeLog,
                                                        NoticeDefaultLogRecord)
        from tendenci.core.base.utils import fieldify
        from tendenci.core.emails.models import Email
        from tendenci.core.site_settings.utils import get_setting

        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        site_contact_name = get_setting('site', 'global', 'sitecontactname')
        site_contact_email = get_setting('site', 'global', 'sitecontactemail')
        site_url = get_setting('site', 'global', 'siteurl')

        corp_replace_str = """
                            <br /><br />
                            <font color="#FF0000">
                            Organizational Members, please contact your company
                            Membership coordinator
                            to ensure that your membership is being renewed.
                            </font>
                            """

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
                template_name = "memberships/notices/email_recap.html"
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
                    email.subject = '%s Membership Notices Distributed' % (
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
                email.subject = 'Error Processing Membership Notices on %s' % (
                                                            site_url)

                email.send()

        def get_script_support_emails():
            admins = getattr(settings, 'ADMINS', None)
            if admins:
                recipients_list = [admin[1] for admin in admins]
                return ','.join(recipients_list)

            return None

        def get_admin_emails():
            admin_emails = get_setting('module', 'memberships',
                                       'membershiprecipients').strip()
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

            if notice.notice_type == 'disapprove':
                status_detail_list = ['disapproved']
            else:
                status_detail_list = ['active', 'expired']
            memberships = MembershipDefault.objects.filter(
                                    status=True,
                                    status_detail__in=status_detail_list
                                    )
            if notice.notice_type == 'join':
                memberships = memberships.filter(
                                    join_dt__year=start_dt.year,
                                    join_dt__month=start_dt.month,
                                    join_dt__day=start_dt.day,
                                    renewal=False)
            elif notice.notice_type == 'renewal':
                memberships = memberships.filter(
                                    renew_dt__year=start_dt.year,
                                    renew_dt__month=start_dt.month,
                                    renew_dt__day=start_dt.day,
                                    renewal=True)
            elif notice.notice_type == 'approve':
                memberships = memberships.filter(
                                    application_approved_denied_dt__year=start_dt.year,
                                    application_approved_denied_dt__month=start_dt.month,
                                    application_approved_denied_dt__day=start_dt.day,
                                    application_approved=True)
            elif notice.notice_type == 'disapprove':
                memberships = memberships.filter(
                                    application_approved_denied_dt__year=start_dt.year,
                                    application_approved_denied_dt__month=start_dt.month,
                                    application_approved_denied_dt__day=start_dt.day,
                                    application_approved=False)
            else:  # 'expire'
                memberships = memberships.filter(
                                    expire_dt__year=start_dt.year,
                                    expire_dt__month=start_dt.month,
                                    expire_dt__day=start_dt.day)

            # filter by membership type
            if notice.membership_type:
                memberships = memberships.filter(
                                membership_type=notice.membership_type)

            memberships_count = memberships.count()

            if memberships_count > 0:
                email.content_type = notice.content_type

                # password
                passwd_str = """
                        If you've forgotten your password or need to reset
                        the auto-generated one, click <a href="%s%s">here</a>
                        and follow the instructions on the page to
                        reset your password.
                        """ % (site_url, reverse('auth_password_reset'))

                global_context = {'sitedisplayname': site_display_name,
                                  'sitecontactname': site_contact_name,
                                  'sitecontactemail': site_contact_email,
                                  'timesubmitted': nowstr,
                                  'password': passwd_str
                                  }

                # log notice sent
                notice_log = NoticeLog(notice=notice,
                                       num_sent=0)
                notice_log.save()
                notice.log = notice_log
                notice.err = ''

                for membership in memberships:
                    try:
                        email_member(notice, membership, global_context)
                        if memberships_count <= 50:
                            notice.members_sent.append(membership)
                        num_sent += 1

                        # log record
                        notice_log_record = NoticeDefaultLogRecord(
                                                notice_log=notice_log,
                                                membership=membership)
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
            user = membership.user

            body = notice.email_content
            context = membership.get_field_items()
            context['membership'] = membership
            context.update(global_context)

            # memberships page ------------
            memberships_page = "%s%s" % \
                (site_url, reverse('profile', args=[membership.user]))

            body = body.replace("[membershiptypeid]",
                                str(membership.membership_type.id))
            body = body.replace("[membershiplink]",
                                '%s' % memberships_page)

            body = body.replace("[renewlink]", memberships_page)

            if membership.expire_dt:
                body = body.replace("[expirationdatetime]",
                                    time.strftime(
                                      "%d-%b-%y %I:%M %p",
                                      membership.expire_dt.timetuple()))
            else:
                body = body.replace("[expirationdatetime]", '')

            # corporate member corp_replace_str
            if membership.corporate_membership_id:
                body = body.replace("<!--[corporatemembernotice]-->",
                                    corp_replace_str)
            else:
                body = body.replace("<!--[corporatemembernotice]-->", "")

            context.update({'membershiptypeid':
                                str(membership.membership_type.id),
                            'membershiplink': memberships_page,
                            'renewlink': memberships_page,
                            'membernumber': membership.member_number,
                            'membershiptype': membership.membership_type.name,
                            })
            if membership.expire_dt:
                context['expirationdatetime'] = time.strftime(
                                            "%d-%b-%y %I:%M %p",
                                            membership.expire_dt.timetuple())

            # corporate member corp_replace_str
            if membership.corporate_membership_id:
                context['corporatemembernotice'] = corp_replace_str

            body = fieldify(body)

            body = '%s <br /><br />%s' % (body, get_footer())

            context = Context(context)
            template = Template(body)
            body = template.render(context)

            email.recipient = user.email
            subject = notice.subject.replace('(name)',
                                        user.get_full_name())
            template = Template(subject)
            subject = template.render(context)

            email.subject = subject
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

