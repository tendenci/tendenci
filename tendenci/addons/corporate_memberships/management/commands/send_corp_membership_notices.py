from datetime import datetime, timedelta
import time
import traceback

from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.template import Context, Template
from django.conf import settings


class Command(BaseCommand):
    """
    Get a list of corporate membership notices from the notice table,
    and send each notice to representatives of corporate memberships
    that meet the criteria.

    Usage: python manage.py send_corp_membership_notices --verbosity 1
    """

    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']
        # first test if we have notices set up
        from tendenci.addons.corporate_memberships.models import Notice
        if not Notice.objects.filter(status=True,
                                     status_detail='active'
                                    ).exclude(
                                    notice_time='attimeof'
                                    ).exists():
            if verbosity > 1:
                print('No notices set up...existing...')
            # no active notices to process. stop here
            return

        from tendenci.addons.corporate_memberships.models import (
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

            if notice.notice_type == 'disapprove':
                status_detail_list = ['inactive']
            else:
                status_detail_list = ['active', 'expired']

            memberships = CorpMembership.objects.filter(
                                    status=True,
                                    status_detail__in=status_detail_list
                                    )
            if notice.notice_type in ['approve_join', 'disapprove_join'
                                      'approve_renewal', 'disapprove_renewal']:
                filters = {'approved_denied_dt__year': start_dt.year,
                           'approved_denied_dt__month': start_dt.month,
                           'approved_denied_dt__day': start_dt.day,
                           'renewal': False,
                           'approved': True
                           }
                if notice.notice_type in ['approve_renewal',
                                          'disapprove_renewal']:
                    filters.update({'renewal': True})
                if notice.notice_type in ['disapprove_join',
                                          'disapprove_renewal']:
                    filters.update({'approved': False})

                memberships = memberships.filter(**filters)
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

                global_context = {'site_display_name': site_display_name,
                                  'site_contact_name': site_contact_name,
                                  'site_contact_email': site_contact_email,
                                  'time_submitted': nowstr,
                                  }

                # log notice sent
                notice_log = NoticeLog(notice=notice,
                                       num_sent=0)
                notice_log.save()
                notice.log = notice_log
                notice.err = ''

                for membership in memberships:
                    try:
                        num_sent += email_member(notice, membership, global_context)
                        if memberships_count <= 50:
                            notice.members_sent.append(membership)

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

            representatives = corp_profile.reps.filter(Q(is_dues_rep=True)|(Q(is_member_rep=True)))
            sent = 0

            for recipient in representatives:
                body = notice.email_content
                context = membership.get_field_items()
                context['membership'] = membership
                context.update(global_context)

                context.update({
                    'rep_first_name': recipient.user.first_name,
                })

                if membership.expiration_dt:
                    body = body.replace("[expirationdatetime]",
                                        time.strftime(
                                          "%d-%b-%y %I:%M %p",
                                          membership.expiration_dt.timetuple()))
                else:
                    body = body.replace("[expirationdatetime]", '')

                context.update({
                    'corporatemembershiptypeid': str(membership.corporate_membership_type.id),
                    'corporatemembershiptype': membership.corporate_membership_type.name,
                    'view_link': "%s%s" % (site_url, membership.get_absolute_url()),
                    'renew_link': "%s%s" % (site_url, membership.get_renewal_url()),
                    'renewed_individuals_list': render_to_string(('notification/corp_memb_notice_email/renew_list.html'),
                                                             {'corp_membership': membership, }),
                })

                body = fieldify(body)

                body = '%s <br /><br />%s' % (body, get_footer())

                context = Context(context)
                template = Template(body)
                body = template.render(context)

                email.recipient = recipient.user.email
                subject = notice.subject.replace('(name)',
                                            corp_profile.name)
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
                sent += 1
                if verbosity > 1:
                    print 'To ', email.recipient, email.subject
            return sent

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

