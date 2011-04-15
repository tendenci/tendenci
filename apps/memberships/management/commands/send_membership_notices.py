from datetime import datetime, timedelta
import time
import traceback
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist


class Command(BaseCommand):
    """
    Get a list of membership notices from the notice table,
    and send each notice to members who meet the criteria. 
    
    To run the command: python manage.py send_membership_notices --verbosity 1
    """
    
    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']
            
        from django.conf import settings
        from memberships.models import Notice, Membership, NoticeLog, NoticeLogRecord
        from emails.models import Email
        from profiles.models import Profile
        from site_settings.utils import get_setting
        
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        site_contact_name = get_setting('site', 'global', 'sitecontactname')
        site_contact_email = get_setting('site', 'global', 'sitecontactemail')
        site_url = get_setting('site', 'global', 'siteurl')
        
        corp_replace_str = """
                            <br /><br />
                            <font color="#FF0000">
                            Organizational Members, please contact your company Membership coordinator
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
            email.recipient = get_script_support_emails()
            if email.recipient:
                template_name = "memberships/notices/email_recap.html"
                try:
                    recap_email_content = render_to_string(template_name, {'notices':notices,
                                                                      'total_sent':total_sent,
                                                                      'site_url': site_url,
                                                                      'site_display_name': site_display_name,
                                                                      'site_contact_name': site_contact_name,
                                                                      'site_contact_email': site_contact_email})
                    email.body = recap_email_content
                    email.content_type = "html"
                    email.subject = '%s Membership Notices Distributed' % site_display_name
                    
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
                email.subject = 'Error Processing Membership Notices on %s' % site_url
                
                email.send()
        
        def get_script_support_emails():
            admins = getattr(settings, 'ADMINS', None) 
            if admins:
                recipients_list = [admin[1] for admin in admins]
                return ','.join(recipients_list)
            
            return None
            
            
        
        def process_notice(notice):
            notice.members_sent = []
            num_sent = 0
            if notice.notice_time == 'before':
                start_dt = now + timedelta(days=notice.num_days)
            else:
                start_dt = now - timedelta(days=notice.num_days)
            
            memberships = Membership.objects.filter(status=1)
            if notice.notice_type == 'join':
                memberships = memberships.filter(join_dt__year=start_dt.year,
                                                join_dt__month=start_dt.month,
                                                join_dt__day=start_dt.day)
            elif notice.notice_type == 'renew':
                memberships = memberships.filter(renew_dt__year=start_dt.year,
                                                renew_dt__month=start_dt.month,
                                                renew_dt__day=start_dt.day)
            else: # 'expire'
                memberships = memberships.filter(expiration_dt__year=start_dt.year,
                                                expiration_dt__month=start_dt.month,
                                                expiration_dt__day=start_dt.day)
            if memberships:
                email.content_type = notice.content_type
                notice.email_content = notice.email_content.replace("[sitedisplayname]", site_display_name)
                notice.email_content = notice.email_content.replace("[sitecontactname]", site_contact_name)
                notice.email_content = notice.email_content.replace("[sitecontactemail]", site_contact_email)
                notice.email_content = notice.email_content.replace("[timesubmitted]", nowstr)
                
                # password
                passwd_str = """
                            If you've forgotten your password or need to reset the auto-generated one,
                            click <a href="%s%s">here</a> and follow the instructions on the page to 
                            reset your password.
                            """ % (site_url, reverse('auth_password_reset'))
                notice.email_content = notice.email_content.replace("[password]", passwd_str)
                
                # log notice sent
                notice_log = NoticeLog(notice=notice,
                                       num_sent=0)
                notice_log.save()
                notice.log = notice_log
                notice.err = ''
                
                memberships_count = memberships.count()
                
                for membership in memberships:
                    try:
                        email_member(notice, membership)
                        if memberships_count <= 50:
                            notice.members_sent.append(membership)
                        num_sent += 1
                        
                        # log record
                        notice_log_record = NoticeLogRecord(notice_log=notice_log,
                                                            membership=membership)
                        notice_log_record.save()
                    except:
                        # catch the exception and email to developers
                        notice.err += traceback.format_exc()
                        
                if num_sent > 0:
                    notice_log.num_sent = num_sent
                    notice_log.save()
                    
            return num_sent    
            
        def email_member(notice, membership):
            user = membership.user
            try:
                profile = user.get_profile()
            except Profile.DoesNotExist:
                profile = Profile.objects.create_profile(user=user)
            
            body = notice.email_content
            body = body.replace("[firstname]", user.first_name)
            body = body.replace("[lastname]", user.last_name)
            body = body.replace("[name]", user.get_full_name())
            body = body.replace("[title]", profile.position_title)
            body = body.replace("[address]", profile.address)
            body = body.replace("[city]", profile.city)
            body = body.replace("[state]", profile.state)
            body = body.replace("[zip]", profile.zipcode)
            body = body.replace("[phone]", profile.phone)
            body = body.replace("[homephone]", profile.home_phone)
            body = body.replace("[fax]", profile.fax)
            body = body.replace("[username]", user.username)
            
            body = body.replace("[membershiptypeid]", str(membership.membership_type.id))
            body = body.replace("[membershiplink]", '%s%s' % (site_url, membership.get_absolute_url()))
            body = body.replace("[renewlink]", '%s%s' % (site_url, membership.get_absolute_url()))
            if membership.expiration_dt:
                body = body.replace("[expirationdatetime]", 
                                    time.strftime("%d-%b-%y %I:%M %p", membership.expiration_dt.timetuple()))
            else:
                body = body.replace("[expirationdatetime]", '')
                
            # corporate member corp_replace_str
            if membership.corporate_membership_id:
                body = body.replace("<!--[corporatemembernotice]-->", corp_replace_str)
            else:
                body = body.replace("<!--[corporatemembernotice]-->", "")
                
            body = '%s <br /><br />%s' % (body, get_footer())
            
            email.recipient = user.email
            email.subject = notice.subject.replace('(name)', user.get_full_name())
            email.body = body
            email.send()
            if verbosity > 1:
                print 'To ', email.recipient, email.subject
            
                
        def get_footer():
            return """
                    This e-mail was generated by Tendenci&reg; Software - a 
                    web based membership management software solution 
                    www.tendenci.com developed by Schipul - The Web Marketing Company
                    """   
                    
                    
        
        exception_str = ""
        
        notices = Notice.objects.filter(status=1, status_detail='active').exclude(notice_time='attimeof')
        
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
                processed_notices = [notice for notice in notices if hasattr(notice, 'log') and notice.log.num_sent>0]
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
                
           
    