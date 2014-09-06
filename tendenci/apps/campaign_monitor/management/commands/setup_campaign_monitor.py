import os
import traceback
from datetime import datetime
import time
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail


class Command(BaseCommand):
    """
    This script is to create a campaign monitor account under the Schipul master account,
    and update setting CAMPAIGNMONITOR_API_CLIENT_ID in the local_settings.py
    with the client_id returned from campaign monitor.
    
    Usage: ./manage.py setup_campaign_monitor --password yourpassword
    
    """
    help = 'Set up a campaign monitor account'
    
    # https://github.com/campaignmonitor/createsend-python/tree/master/createsend
    # http://www.campaignmonitor.com/api/clients/ 
    
    option_list = BaseCommand.option_list + (
        make_option('--password',
            action='store',
            dest='password',
            default=None,
            help='Password of the campaign monitor account being created'),
        )
      
    def handle(self, *args, **options):
        from createsend import CreateSend, Client, List, Subscriber, \
                BadRequest, Unauthorized
        from tendenci.apps.site_settings.utils import get_setting
        from tendenci.apps.emails.models import Email
            
            
        def get_contact_email():
            site_name = get_setting('site', 'global', 'sitedisplayname')
            email = 't5+%s@schipul.com' % site_name.replace(' ', '')
            return email 
    
        def setup_cm_account(password=''):
            # check if already setup
            client_id =  getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', '')
            if not client_id or client_id == '[CAMPAIGNMONITOR_API_CLIENT_ID]':
                cs = CreateSend()
                company_name = get_setting('site', 'global', 'sitedisplayname')
                #contact_name = get_setting('site', 'global', 'admincontactname')
                #contact_email = get_setting('site', 'global', 'admincontactemail')
                contact_name = "Schipul Client"
                contact_email = get_contact_email()
                if not contact_email:
                    raise ValueError("Invalid Email address.")
                #timezone = get_setting('site', 'global', 'defaulttimezone')
                # country - must exist on campaign monitor
                country = 'United States of America'
                
                # timezone - must use the format specified by campaign monitor
                timezone = "(GMT-06:00) Central Time (US & Canada)"
                
                api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None) 
                CreateSend.api_key = api_key
                
                # check if this company already exists on campaign monitor
                # if it does, raise an error
                
                clients = cs.clients()
                cm_client_id = None
                
                for cl in clients:
                    if cl.Name == company_name:
                        #cm_client_id = cl.ClientID
                        #break
                        raise ValueError('Company name "%s" already exists on campaign monitor.' % company_name)
                    
                if not cm_client_id:
                    # 1) Create an account
                    cl = Client()
                    cm_client_id = cl.create(company_name, contact_name, contact_email, timezone, country)
                    cl = Client(cm_client_id)
                    
                    # 2) Set access with username and password
                    # access level = 63  full access
                    username = company_name.replace(' ', '')
                    if not password:
                        # generate a random password with 6 in length
                        allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789()#$%'
                        password = User.objects.make_random_password(length=6, allowed_chars=allowed_chars)
                    
                    cl.set_access(username, password, 63)
                    
                    # 3) Set up billing - client will pay monthly
                    #cl.set_payg_billing('USD', True, True, 0)
                    cl.set_monthly_billing('USD', True, 0)
                    
                    # send an email to t5@schipul.com
                    now = datetime.now()
                    now_str = now.strftime('%m/%d/%Y %H:%M')
                    sender = get_setting('site', 'global', 'siteemailnoreplyaddress') or settings.DEFAULT_FROM_EMAIL
                    recipient = 't5@schipul.com'
                    subject = 'Campaign Monitor New client Account "%s" Created' % company_name
                    email_body = """Company Name: %s
                                    \n\nContact Name: %s
                                    \n\nContact Email: %s
                                    \n\n\nThanks,\n%s\n
                                """ % (company_name, contact_name, contact_email, now_str)
                    send_mail(subject, email_body, sender, [recipient], fail_silently=True)
                    
                                    
                
                # add/update the client_id in the local_settings.py
                local_setting_file = os.path.join(getattr(settings, 'PROJECT_ROOT'), 'settings.py')
                f = open(local_setting_file, 'r')
                content = f.read()
                if client_id == '[CAMPAIGNMONITOR_API_CLIENT_ID]':
                    content = content.replace('[CAMPAIGNMONITOR_API_CLIENT_ID]', cm_client_id)
                else:
                    content = "%s\nCAMPAIGNMONITOR_API_CLIENT_ID='%s'\n" % (content, cm_client_id)
                f.close()
                f = open(local_setting_file, 'w')
                f.write(content)
                f.close()
                
                print('Success!')
                
            else:
                print('Already has a campaign monitor account')
        
        
        def email_script_errors(err_msg):
            """Send error message to us in case of an error.
            """
            email = Email()
            email.sender = get_setting('site', 'global', 'siteemailnoreplyaddress')
            email.sender_display = get_setting('site', 'global', 'sitedisplayname')
            site_url = get_setting('site', 'global', 'siteurl')
        
            now = datetime.now()
            nowstr = time.strftime("%d-%b-%y %I:%M %p", now.timetuple())
            email.recipient = get_script_support_emails()
            if email.recipient:
                email.body = '%s \n\nTime Submitted: %s\n' % (err_msg, nowstr)
                email.content_type = "text"
                email.subject = 'Error Setting Up Campaign Monitor Account on New Site %s' % site_url
                
                email.send()
        
        def get_script_support_emails():
            admins = getattr(settings, 'ADMINS', None) 
            if admins:
                recipients_list = [admin[1] for admin in admins]
                return ','.join(recipients_list)
            
            return None
        
        try:
            password = options['password']
            setup_cm_account(password)
        except:
            err_msg = traceback.format_exc()
            email_script_errors(err_msg)
            

            