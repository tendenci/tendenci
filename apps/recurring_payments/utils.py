from datetime import datetime
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from dateutil.relativedelta import relativedelta
from emails.models import Email
from site_settings.utils import get_setting
from profiles.models import Profile
from recurring_payments.models import RecurringPayment, PaymentProfile
from recurring_payments.authnet.cim import CIMCustomerProfile, CIMHostedProfilePage
from recurring_payments.authnet.utils import get_token
        
  
class RecurringPaymentEmailNotices(object):
    def __init__(self):
        self.site_display_name = get_setting('site', 'global', 'sitedisplayname')
        self.site_contact_name = get_setting('site', 'global', 'sitecontactname')
        self.site_contact_email = get_setting('site', 'global', 'sitecontactemail')
        self.site_url = get_setting('site', 'global', 'siteurl')
    
        self.email = Email()
        self.email.sender = get_setting('site', 'global', 'siteemailnoreplyaddress')
        self.email.sender_display = self.site_display_name
        self.email.reply_to = self.site_contact_email
        
        self.admin_emails = self.get_admin_emails() 

    def get_admin_emails(self):
        admin_emails = (get_setting('site', 'global', 'admincontactemail')).split(',')
            
        if admin_emails:
            admin_emails = ','.join(admin_emails)
            
        return admin_emails
    
    def get_script_support_emails(self):
        admins = getattr(settings, 'ADMINS', None) 
        if admins:
            recipients_list = [admin[1] for admin in admins]
            return ','.join(recipients_list)
        
        return None
        
    def email_script_support_transaction_error(self, payment_transaction):
        """if there is an error other than transaction not being approved, notify us.
        """
        self.email.recipient = self.get_script_support_emails()
        if self.email.recipient:
            template_name = "recurring_payments/email_script_support_transaction.html"
            try:
                email_content = render_to_string(template_name, 
                                               {'pt':payment_transaction,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                self.email.subject = 'Recurring payment transaction error on %s' % ( 
                                                                            self.site_display_name)
                
                self.email.send()
            except TemplateDoesNotExist:
                pass
        
    def email_admins_transaction_result(self, payment_transaction):
        """Send admins the result after the transaction is processed.
        """
        self.email.recipient = self.admin_emails
        if self.email.recipient:
            template_name = "recurring_payments/email_admins_transaction.html"
            try:
                email_content = render_to_string(template_name, 
                                               {'pt':payment_transaction,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                self.email.subject = 'Recurring payment transaction processed on %s' % ( 
                                                                            self.site_display_name)
                
                self.email.send()
            except TemplateDoesNotExist:
                pass

    def email_customer_transaction_result(self, payment_transaction):
        """Send customer an email after the transaction is processed.
        """
        self.email.recipient = payment_transaction.recurring_payment.user.email
        if self.email.recipient:
            template_name = "recurring_payments/email_customer_transaction.html"
            try:
                email_content = render_to_string(template_name, 
                                               {'pt':payment_transaction,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                if payment_transaction.status:
                    self.email.subject = 'Payment received on %s' % ( 
                                                            self.site_display_name)
                else:
                    self.email.subject = 'Payment failed on %s' % ( 
                                                            self.site_display_name)
                
                self.email.send()
            except TemplateDoesNotExist:
                pass

    def email_admins_no_payment_profile(self, recurring_payment):
        """Notify admin that payment method hasn't been setup yet for this recurring payment entry.
        """
        self.email.recipient = self.admin_emails
        if self.email.recipient:
            template_name = "recurring_payments/email_admins_no_payment_profile.html"
            try:
                email_content = render_to_string(template_name, 
                                               {'rp':recurring_payment,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                self.email.subject = 'Payment method not setup for %s on %s' % ( 
                                    recurring_payment , self.site_display_name)
                
                self.email.send()
            except TemplateDoesNotExist:
                pass

    def email_customer_no_payment_profile(self, recurring_payment):
        """Notify customer that payment method hasn't been setup yet for this recurring payment entry.
        """
        self.email.recipient = recurring_payment.user.email
        if self.email.recipient:
            template_name = "recurring_payments/email_customer_no_payment_profile.html"
            try:
                email_content = render_to_string(template_name, 
                                               {'rp':recurring_payment,
                                                'site_display_name': self.site_display_name,
                                                'site_url': self.site_url
                                                })
                self.email.body = email_content
                self.email.content_type = "html"
                self.email.subject = 'Please update your payment method for %s on %s' % ( 
                                    recurring_payment.description, self.site_display_name)
                
                self.email.send()
            except TemplateDoesNotExist:
                pass
            
            
def api_add_rp(data):
    """Create a recurrring payment account. Accepted format: json
    
    Input fields:
        email - required
        description - required
        payment_amount - required
        billing_period - optional, default to 'month'
        billing_frequency - optional, default to 1
        billing_start_dt - optional, default to today
        num_days - optional, default to 0
        has_trial_period - optional, default to False
        trial_period_start_dt - optional, default to today
        trial_period_end_dt - optional, default to today
        trial_amount - optional, default to 0
        
    Output:
        rp_id - a recurring payment id
        result_code
    """
    ALLOWED_FIELES = ('email',
                      'description',
                      'payment_amount',
                      'billing_period',
                      'billing_frequency',
                      'billing_start_dt',
                      'num_days',
                      'has_trial_period',
                      'trial_period_start_dt',
                      'trial_period_end_dt',
                      'trial_amount',
                      )
    from decimal import Decimal
    from django.core.validators import email_re
    import dateutil.parser as dparser
    from imports.utils import get_unique_username
    
    email = data.get('email', '')
    payment_amount = data.get('payment_amount', '')
    try:
        payment_amount = Decimal(payment_amount)
    except:
        payment_amount = 0
    
    
    if not all([email_re.match(email), 
                data.has_key('description'),
                payment_amount>0]):
        return False, {}
    
    
    rp = RecurringPayment()
    for key, value in data.items():
        if key in ALLOWED_FIELES:
            if hasattr(rp, key):
                exec('rp.%s="%s"' % (key, value))
            
    if rp.billing_start_dt:
        try:
            rp.billing_start_dt = dparser.parse(rp.billing_start_dt)
        except:
            rp.billing_start_dt = datetime.now()
    else:
        rp.billing_start_dt = datetime.now()
    if rp.trial_period_start_dt:
        try:
            rp.trial_period_start_dt = dparser.parse(rp.trial_period_start_dt)
        except:
            rp.trial_period_start_dt = datetime.now()
    
    if rp.trial_period_end_dt:
        try:
            rp.trial_period_end_dt = dparser.parse(rp.trial_period_end_dt)
        except:
            rp.trial_period_end_dt = datetime.now()
        
    rp.payment_amount = Decimal(rp.payment_amount)
    
    try:
        rp.billing_frequency = int(rp.billing_frequency)
    except:
        rp.billing_frequency = 1
    try:
        rp.num_days = int(rp.num_days)
    except:
        rp.num_days = 1
    if rp.has_trial_period in ['True', '1',  True, 1] and all([rp.trial_period_start_dt,
                                                              rp.trial_period_end_dt]):
        rp.has_trial_period = True
    else:
        rp.has_trial_period = False
        
    # start the real work
    
#    # get or create a user account with this email
#    users = User.objects.filter(email=email)
#    if users:
#        u = users[0]
#    else:

    # always create a new user account - This is very important!
    # it is to prevent hacker from trying to use somebody else's account. 
    u = User()
    u.email=email
    u.username = data.get('username', '')
    if not u.username:
        u.username = email.split('@')[0]
    u.username = get_unique_username(u)
    raw_password = data.get('password', '')
    if not raw_password:
        raw_password = User.objects.make_random_password(length=8)
    u.set_password(raw_password)
    u.first_name = data.get('first_name', '')
    u.last_name = data.get('last_name', '')
    u.is_staff = False
    u.is_superuser = False
    u.save()
    
#    profile = Profile.objects.create(
#           user=u, 
#           creator=u, 
#           creator_username=u.username,
#           owner=u, 
#           owner_username=u.username, 
#           email=u.email
#        )
    
    # add a recurring payment entry for this user
    rp.user = u
    rp.save()
    
    return True, {'rp_id': rp.id}
        
        
def api_get_rp_token(data):
    """Get the token for using authorize.net hosted profile page
        Accepted format: json
    
    Input fields:
        rp_id - required
        iframe_communicator_url
        
    Output:
        token
        gateway_error
        payment_profile_id
        result_code
    """
    rp_id = data.get('rp_id', 0)
    iframe_communicator_url = data.get('iframe_communicator_url', '')
    
    try:
        rp = RecurringPayment.objects.get(id=int(rp_id))
    except:
        return False, {}
    
    token, gateway_error = get_token(rp, CIMCustomerProfile, 
                                     CIMHostedProfilePage, 
                                     iframe_communicator_url)
    
    d = {'token': token,
         'gateway_error': gateway_error}
    
    # also pass the payment_profile_id
    payment_profiles = PaymentProfile.objects.filter(customer_profile_id=rp.customer_profile_id, 
                                                    status=1, 
                                                    status_detail='active')
    if payment_profiles:
        payment_profile_id = (payment_profiles[0]).payment_profile_id
    else:
        payment_profile_id = ''
        
    d['payment_profile_id'] = payment_profile_id
    
    
    if gateway_error:
        status = False
    else:
        status = True
        
    return status, d


def api_verify_rp_payment_profile(data):
    """Verify if this recurring payment account
        has a valid payment profile.
        Accepted format: json
    
    Input fields:
        rp_id - required
        
    Output:
        has_payment_profile
        result_code
    """
    rp_id = data.get('rp_id', 0)
    
    try:
        rp = RecurringPayment.objects.get(id=int(rp_id))
    except:
        return False, {}
    
    d = {}
    pay_now = data.get('pay_now', '')
    if pay_now == 'yes': pay_now = True
    else: pay_now = False
    
    # pp - customer payment_profile
    validation_mode=''
    if not pay_now: 
        validation_mode='liveMode'
        
    is_valid = True
        
    valid_cpp_ids, invalid_cpp_ids = rp.populate_payment_profile(validation_mode=validation_mode)
    if valid_cpp_ids:
        d['valid_cpp_id'] = valid_cpp_ids[0]
        if pay_now:
            # make a transaction NOW
            billing_cycle = {'start': rp.billing_start_dt, 
                             'end': rp.billing_start_dt + relativedelta(months=rp.billing_frequency)}
            billing_dt = datetime.now()
            rp_invoice = rp.create_invoice(billing_cycle, billing_dt)
            payment_transaction = rp_invoice.make_payment_transaction(d['valid_cpp_id'])
            if not payment_transaction.status:
                d['invalid_cpp_id'] = d['valid_cpp_id']
                d['valid_cpp_id'] = ''
                is_valid = False
            else:
                # send out the invoice view page
                d['receipt_url'] = '%s%s' % (get_setting('site', 'global', 'siteurl'), 
                                             reverse('recurring_payment.transaction_receipt', 
                                                args=[rp.id, 
                                                payment_transaction.id,
                                                rp.guid]))
            
    
    if invalid_cpp_ids:
        d['invalid_cpp_id']= invalid_cpp_ids[0]
                  
    return is_valid, d


    
        
    
    
        
    
    
    
            
    