import uuid
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from dateutil.relativedelta import relativedelta
from invoices.models import Invoice
from profiles.models import Profile
from recurring_payments.authnet.cim import (CIMCustomerProfile,
                                            CIMCustomerProfileTransaction)
from payments.models import Payment


class RecurringPayment(models.Model):
    guid = models.CharField(max_length=50)
    # gateway assigned ID associated with the customer profile
    customer_profile_id = models.CharField(max_length=100, default='')
    user = models.ForeignKey(User, related_name="recurring_payment_user",
                             verbose_name=_('Customer'),  null=True)
    description = models.CharField(max_length=100)
    # with object_content_type and object_content_id, we can apply the recurring 
    # payment to other modules such as memberships, jobs, etc.
    object_content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_content_id = models.IntegerField(default=0, blank=True, null=True)

    billing_period = models.CharField(max_length=50, choices=(('month', _('Month')),
                                                            ('year', _('Year')),
                                                            ('week', _('Week')),
                                                            ('day', _('Day')),
                                                            ),
                                        default='month')
    billing_frequency = models.IntegerField(default=1)
    billing_start_dt = models.DateTimeField(_("Start date"), help_text=_("The initial start date for the recurring payments."))
    #billing_cycle_start_dt = models.DateTimeField(_("Billing cycle start date"))
    #billing_cycle_end_dt = models.DateTimeField(_('Billing cycle end date'), blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    has_trial_period = models.BooleanField(default=0)
    trial_period_start_dt = models.DateTimeField(_('Trial period start date'), blank=True, null=True)
    trial_period_end_dt = models.DateTimeField(_('Trial period end date'), blank=True, null=True)
    trial_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    next_billing_dt = models.DateTimeField(blank=True, null=True)
    last_payment_received_dt = models.DateTimeField(blank=True, null=True)
    num_billing_cycle_completed = models.IntegerField(default=0, blank=True, null=True)
    num_billing_cycle_failed = models.IntegerField(default=0, blank=True, null=True)
    failed_reason = models.CharField(max_length=200, default='', blank=True, null=True)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="recurring_payment_creator",  null=True)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="recurring_payment_owner", null=True)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='active')
    status = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(RecurringPayment, self).save(*args, **kwargs)
        
    def populate_payment_profile(self, *args, **kwargs):
        """
        Check payment gateway for the payment profiles for this customer 
        and store the payment profile info locally
        """
        customer_profile = CIMCustomerProfile(self.customer_profile_id)
        success, response_d = customer_profile.get()
        
        if success:
            cim_payment_profiles = response_d['profile']['payment_profiles']
            if not type(cim_payment_profiles) is list:
                cim_payment_profiles = list([cim_payment_profiles])
            for cim_payment_profile in cim_payment_profiles:
                customer_payment_profile_id = cim_payment_profile['customer_payment_profile_id']
                
                # check if already exists, if not, insert to payment profiles table
                payment_profile_exists = PaymentProfile.objects.filter(
                                                payment_profile_id=customer_payment_profile_id
                                                ).exists()
                
                if not payment_profile_exists:
                
                    payment_profile = PaymentProfile(recurring_payment=self,
                                                     payment_profile_id=customer_payment_profile_id,
                                                     creator=self.user,
                                                     owner=self.user,
                                                     creator_username= self.user.username,
                                                     owner_username = self.user.username,
                                                     )
                    if cim_payment_profile['payment'].has_key('credit_card') and \
                                cim_payment_profile['payment']['credit_card'].has_key('card_number'):
                        print cim_payment_profile['payment']
                        card_num = cim_payment_profile['payment']['credit_card']['card_number'][-4:]
                        payment_profile.card_num = card_num
                    payment_profile.save()  
        
        
        
        
    def within_trial_period(self):
        if all([self.has_trial_period, self.trial_period_start_dt, self.trial_period_end_dt]):
            now = datetime.now()
            return now <= self.trial_period_end_dt
        return False
    
    def get_next_billing_cycle(self, last_billing_cycle=None):
        if self.billing_period == 'year':
            timedelta = relativedelta(years=self.billing_frequency)
        elif self.billing_period == 'month':
            timedelta = relativedelta(months=self.billing_frequency)
        elif self.billing_period == 'day':
            timedelta = relativedelta(days=self.billing_frequency)
        elif self.billing_period == 'week':
            timedelta = relativedelta(days=self.billing_frequency*7)
        else:
            timedelta = relativedelta(months=self.billing_frequency)
                    
        if not last_billing_cycle:
            if self.within_trial_period():
                return (self.trial_period_start_dt, self.trial_period_end_dt)
            else:
                billing_cycle_start = self.billing_start_dt
                billing_cycle_end = billing_cycle_start + timedelta
        else:
            billing_cycle_start = last_billing_cycle['end'] + relativedelta(days=1)
            billing_cycle_end = billing_cycle_start + timedelta
            
        
        return (billing_cycle_start, billing_cycle_end)  
    
    def get_last_billing_cycle(self):
        rp_invs = RecurringPaymentInvoice.objects.filter(
                            recurring_payment=self).order_by('-billing_cycle_start_dt')
        if rp_invs:
            return (rp_invs[0].billing_cycle_start_dt, rp_invs[0].billing_cycle_end_dt)
        else:
            return None
        
    def billing_cycle_t2d(self, billing_cycle):
        if billing_cycle:
            billing_cycle = dict(zip(('start', 'end'), billing_cycle))
        return billing_cycle
        
        
    def check_and_generate_invoices(self):
        """
        Check and generate invoices if needed.
        """
        now = datetime.now()
        last_billing_cycle = self.billing_cycle_t2d(self.get_last_billing_cycle())
            
        next_billing_cycle = self.billing_cycle_t2d(self.get_next_billing_cycle(last_billing_cycle))
        
        while next_billing_cycle['start'] <= now + relativedelta(days=10):
            self.create_invoice(next_billing_cycle)
            last_billing_cycle = next_billing_cycle
            next_billing_cycle = self.billing_cycle_t2d(self.get_next_billing_cycle(last_billing_cycle)) 
        
    def create_invoice(self, billing_cycle):
        """
        Create an invoice and update the next_billing_dt for this recurring payment.
        """
        try:
            profile = self.user.get_profile()
        except Profile.DoesNotExist:
            profile = Profile.objects.create_profile(user=self.user)
        
        if self.within_trial_period():
            amount = self.trial_amount
        else:
            amount = self.payment_amount
            
        self.next_billing_dt = billing_cycle['start']
        
        self.save()
            
        inv = Invoice()
        inv.due_date = self.next_billing_dt
        inv.ship_date = self.next_billing_dt
        inv.object_type = ContentType.objects.get(app_label=self._meta.app_label, 
                                                  model=self._meta.module_name)
        inv.object_id = self.id
        inv.title = "Recurring Payment Invoice"
        inv.bill_to = self.user.get_full_name()
        inv.bill_to_company = profile.company
        inv.bill_to_address = profile.address
        inv.bill_to_city = profile.city
        inv.bill_to_state = profile.state
        inv.bill_to_zip_code = profile.zipcode
        inv.bill_to_country = profile.country
        inv.bill_to_phone = profile.phone
        inv.bill_to_email = profile.email
        inv.status = True
        
        inv.total = amount
        inv.subtotal = inv.total
        inv.balance = inv.total
        inv.estimate = 1
        inv.status_detail = 'estimate'
        inv.save(self.user)
        
        rp_invoice = RecurringPaymentInvoice(
                             recurring_payment=self,
                             invoice=inv,
                             billing_cycle_start_dt=billing_cycle['start'],
                             billing_cycle_end_dt=billing_cycle['end'],
                             billing_dt=billing_cycle['start']
                                             )
        rp_invoice.save()
        
        return rp_invoice
        
        
        
class RecurringPaymentInvoice(models.Model):
    recurring_payment =  models.ForeignKey(RecurringPayment)
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    billing_cycle_start_dt = models.DateTimeField(_("Billing cycle start date"), blank=True, null=True)
    billing_cycle_end_dt = models.DateTimeField(_('Billing cycle end date'), blank=True, null=True)
    # billing date is same as due date in invoice
    # also billing_dt = billing_cycle_start_dt
    billing_dt = models.DateTimeField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    #is_paid = models.BooleanField(default=False)
    
    def make_payment_transaction(self, payment_profile_id):
        """
        Make a payment transaction. This includes:
        1) Make an API call createCustomerProfileTransactionRequest
        2) Create a payment transaction entry
        3) Create a payment entry
        4) If the transaction is successful, mark payment as paid
        """
        cpt = CIMCustomerProfileTransaction(self.recurring_payment.customer_profile_id,
                                            payment_profile_id)
        amount = self.invoice.balance
        
        d = {'amount': amount,
             }
        success, response_d = cpt.create(**d)
       
        # create a payment transaction record 
        payment_transaction = PaymentTransaction(
                                    recurring_payment = self.recurring_payment,
                                    payment_profile_id = payment_profile_id,
                                    trans_type='auth_capture',
                                    amount=amount,
                                    status_detail=success)
       
        if success:
            # create a payment record
            payment = Payment()
    
            payment.payments_pop_by_invoice_user(self.recurring_payment.user, 
                                                 self.invoice, 
                                                 self.invoice.guid)
            payment.response_code = '1'
            payment.response_reason_code = '1'
            payment.mark_as_paid()
            payment.save()
            payment.invoice.make_payment(self.recurring_payment.user, payment.amount)
            
            payment_transaction.paymentid = payment.id
            
        payment_transaction.save()
        return success, response_d
     

class PaymentProfile(models.Model):
    recurring_payment =  models.ForeignKey(RecurringPayment)
    # assigned by gateway
    payment_profile_id = models.CharField(max_length=100, unique=True)
    card_type = models.CharField(max_length=50, null=True)
    # last 4 digits of card number
    card_num = models.CharField(max_length=4, null=True)
    expiration_dt = models.DateTimeField(blank=True, null=True)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="payment_profile_creator",  null=True)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="payment_profile_owner", null=True)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='active')
    status = models.BooleanField(default=True)


class PaymentTransaction(models.Model):
    recurring_payment =  models.ForeignKey(RecurringPayment)
    payment_profile_id = models.CharField(max_length=100, default='')
    # trans_type - capture, refund or void
    trans_type  = models.CharField(max_length=50, null=True) 
    # refid       
    paymentid =  models.IntegerField(default=0)       
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="payment_transaction_creator",  null=True)

    status_detail = models.CharField(max_length=50,  null=True)