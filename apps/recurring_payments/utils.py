from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.conf import settings
from emails.models import Email
from site_settings.utils import get_setting
        
  
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
            
    