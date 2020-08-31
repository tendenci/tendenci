
from datetime import datetime, timedelta
import time
import traceback

from django.core.management.base import BaseCommand
from django.urls import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from django.template import engines, TemplateDoesNotExist
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
        from tendenci.apps.corporate_memberships.models import Notice
        if not Notice.objects.filter(status=True,
                                     status_detail='active'
                                    ).exclude(
                                    notice_time='attimeof'
                                    ).exists():
            if verbosity > 1:
                print('No notices set up...existing...')
            # no active notices to process. stop here
            return

        from tendenci.apps.corporate_memberships.models import (
            CorpMembership, CorpMembershipApp,
            NoticeLog,
            NoticeLogRecord)
        from tendenci.apps.notifications import models as notification
        from tendenci.apps.base.utils import fieldify
        from tendenci.apps.site_settings.utils import get_setting

        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        site_contact_name = get_setting('site', 'global', 'sitecontactname')
        site_contact_email = get_setting('site', 'global', 'sitecontactemail')
        site_url = get_setting('site', 'global', 'siteurl')

        email_context = {
            'sender':get_setting('site', 'global', 'siteemailnoreplyaddress'),
            'sender_display':site_display_name,
            'reply_to':site_contact_email}

        now = datetime.now()
        nowstr = time.strftime("%d-%b-%y %I:%M %p", now.timetuple())

        def email_admins_recap(notices, total_sent):
            """Send admins recap after the notices were processed.
            """
            recap_recipient = get_admin_emails()
            if recap_recipient:
                template_name = "corporate_memberships/notices/email_recap.html"
                try:
                    recap_email_content = render_to_string(
                               template_name=template_name,
                               context={'notices': notices,
                              'total_sent': total_sent,
                              'site_url': site_url,
                              'site_display_name': site_display_name,
                              'site_contact_name': site_contact_name,
                              'site_contact_email': site_contact_email})
                    recap_subject = '%s Corporate Membership Notices Distributed' % (
                                                    site_display_name)
                    email_context.update({
                        'subject':recap_subject,
                        'content': recap_email_content,
                        'content_type':"html"})

                    notification.send_emails(recap_recipient, 'corp_memb_notice_email',
                                             email_context)
                except (TemplateDoesNotExist, IOError):
                    pass

        def email_script_errors(err_msg):
            """Send error message to us if any.
            """
            script_recipient = get_script_support_emails()
            if script_recipient:
                email_context.update({
                    'subject':'Error Processing Corporate Membership Notices on %s' % (
                                                            site_url),
                    'content':'%s \n\nTime Submitted: %s\n' % (err_msg, nowstr),
                    'content_type':"text"})

                notification.send_emails(script_recipient, 'corp_memb_notice_email',
                                         email_context)

        def get_script_support_emails():
            admins = getattr(settings, 'ADMINS', None)
            if admins:
                recipients_list = [admin[1] for admin in admins]
                return recipients_list
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
                email_context.update({'content_type':notice.content_type})

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
                        print(traceback.format_exc())

                if num_sent > 0:
                    notice_log.num_sent = num_sent
                    notice_log.save()

            return num_sent

        def email_member(notice, membership, global_context):
            corp_profile = membership.corp_profile
            representatives = corp_profile.reps.filter(Q(is_dues_rep=True) | (Q(is_member_rep=True)))
            sent = 0

            corp_app = CorpMembershipApp.objects.current_app()
            authentication_info = render_to_string(
                template_name='notification/corp_memb_notice_email/auth_info.html',
                context={'corp_membership': membership,
                 'corp_app': corp_app})
            individuals_join_url = '%s%s' % (site_url,
                                             reverse('membership_default.corp_pre_add',
                                                     args=[membership.id]))
            if membership.expiration_dt:
                expire_dt = time.strftime("%d-%b-%y %I:%M %p",
                                          membership.expiration_dt.timetuple())
            else:
                expire_dt = ''

            if membership.payment_method:
                payment_method = membership.payment_method.human_name
            else:
                payment_method = ''

            if membership.renewal:
                renewed_individuals_list = render_to_string(
                    template_name='notification/corp_memb_notice_email/renew_list.html',
                    context={'corp_membership': membership})
                total_individuals_renewed = membership.indivmembershiprenewentry_set.count()
            else:
                renewed_individuals_list = ''
                total_individuals_renewed = ''

            if membership.invoice:
                invoice_link = '%s%s' % (site_url,
                                         membership.invoice.get_absolute_url())
            else:
                invoice_link = ''

            if membership.corp_profile.directory:
                directory_url = '{0}{1}'.format(site_url, reverse('directory',
                                                     args=[membership.corp_profile.directory.slug]))
                directory_edit_url = '{0}{1}'.format(site_url, reverse('directory.edit',
                                    args=[membership.corp_profile.directory.id]))
            else:
                directory_url = ''
                directory_edit_url = ''

            global_context.update({
                'name': corp_profile.name,
                'email': corp_profile.email,
                'expire_dt': expire_dt,
                'payment_method': payment_method,
                'renewed_individuals_list': renewed_individuals_list,
                'total_individuals_renewed': total_individuals_renewed,
                'view_link': "%s%s" % (site_url, membership.get_absolute_url()),
                'renew_link': "%s%s" % (site_url, membership.get_renewal_url()),
                'invoice_link': invoice_link,
                'authentication_info': authentication_info,
                'individuals_join_url': individuals_join_url,
                'directory_url': directory_url,
                'directory_edit_url': directory_edit_url,
            })
            
            

            for recipient in representatives:
                body = notice.email_content
                context = membership.get_field_items()
                context['membership'] = membership
                context.update(global_context)

                context.update({
                    'rep_first_name': recipient.user.first_name,
                })

                body = fieldify(body)

                body = body + ' <br /><br />{% include "email_footer.html" %}'

                template = engines['django'].from_string(body)
                body = template.render(context=context)

                email_recipient = recipient.user.email
                subject = notice.subject.replace('(name)',
                                            corp_profile.name)
                template = engines['django'].from_string(subject)
                subject = template.render(context=context)

                email_context.update({
                    'subject':subject,
                    'content':body})

                if notice.sender:
                    email_context.update({
                        #'sender':notice.sender,
                        'reply_to':notice.sender})
                if notice.sender_display:
                    email_context.update({'sender_display':notice.sender_display})

                notification.send_emails([email_recipient], 'corp_memb_notice_email',
                                         email_context)
                sent += 1
                if verbosity > 1:
                    print('To ', email_recipient, subject)
            return sent

        exception_str = ""

        notices = Notice.objects.filter(status=True, status_detail='active'
                                    ).exclude(notice_time='attimeof')

        if notices:
            if verbosity > 1:
                print("Start sending out notices to members:")
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
                print('Total notice processed: %d' % (total_notices))
                print('Total email sent: %d' % (total_sent))
                print("Done")
        else:
            if verbosity > 1:
                print("No notices on the site.")
