
import uuid
import re
from datetime import datetime, timedelta
from decimal import Decimal
import math
import stripe
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.conf import settings

from dateutil.relativedelta import relativedelta
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.profiles.models import Profile
from tendenci.apps.recurring_payments.managers import RecurringPaymentManager
from tendenci.apps.recurring_payments.authnet.cim import (CIMCustomerProfile,
                                            CIMCustomerPaymentProfile,
                                            CIMCustomerProfileTransaction)
from tendenci.apps.recurring_payments.authnet.utils import payment_update_from_response
from tendenci.apps.recurring_payments.authnet.utils import direct_response_dict
from tendenci.apps.payments.models import Payment
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.payments.stripe.utils import stripe_set_app_info


BILLING_PERIOD_CHOICES = (
                        ('month', _('Month(s)')),
                        ('year', _('Year(s)')),
                        ('week', _('Week(s)')),
                        ('day', _('Day(s)')),
                        )

STATUS_DETAIL_CHOICES = (
                        ('active', _('Active')),
                        ('inactive', _('Inactive')),
                        ('disabled', _('Disabled')),
                        )

DUE_SORE_CHOICES = (
                    ('start', _('start')),
                    ('end', _('end')),
                    )


class RecurringPayment(models.Model):
    PLATFORM_CHOICES = (('authorizenet', 'authorizenet'),
                        ('stripe', 'stripe'))
    guid = models.CharField(max_length=50)
    platform = models.CharField(max_length=50, blank=True, default='authorizenet')
    # gateway assigned ID associated with the customer profile
    customer_profile_id = models.CharField(max_length=100, default='')
    user = models.ForeignKey(User, related_name="recurring_payments",
                             verbose_name=_('Customer'),  null=True, on_delete=models.SET_NULL)
    url = models.CharField(_('Website URL'), max_length=100, default='', blank=True, null=True)
    description = models.CharField(_('Description'), max_length=100, help_text=_("Use a short term, example: web hosting"))
    # with object_content_type and object_content_id, we can apply the recurring
    # payment to other modules such as memberships, jobs, etc.
    object_content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.SET_NULL)
    object_content_id = models.IntegerField(default=0, blank=True, null=True)

    billing_period = models.CharField(max_length=50, choices=BILLING_PERIOD_CHOICES,
                                        default='month')
    billing_frequency = models.IntegerField(default=1)
    billing_start_dt = models.DateTimeField(_("Initial billing cycle start date"),
                                            help_text=_("The initial start date for the recurring payments."+
                                            "That is, the start date of the first billing cycle."))
    # num days after billing cycle end date to determine billing_dt or payment due date
    num_days = models.IntegerField(default=0)
#    due_borf = models.CharField(_("Before or after"), max_length=20,
#                                   choices=DUE_BORF_CHOICES, default='before')
    due_sore = models.CharField(_("Billing cycle start or end date"), max_length=20,
                                   choices=DUE_SORE_CHOICES, default='start')

    #billing_cycle_start_dt = models.DateTimeField(_("Billing cycle start date"))
    #billing_cycle_end_dt = models.DateTimeField(_('Billing cycle end date'), blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax_exempt =models.BooleanField(default=True)
    taxable = models.BooleanField(default=False)
    tax_rate = models.DecimalField(blank=True, max_digits=7, decimal_places=6, default=0,
                                   help_text=_('Example: 0.0825 for 8.25%.'))
    has_trial_period = models.BooleanField(default=False)
    trial_period_start_dt = models.DateTimeField(_('Trial period start date'), blank=True, null=True)
    trial_period_end_dt = models.DateTimeField(_('Trial period end date'), blank=True, null=True)
    trial_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    next_billing_dt = models.DateTimeField(blank=True, null=True)
    last_payment_received_dt = models.DateTimeField(blank=True, null=True)
    num_billing_cycle_completed = models.IntegerField(default=0, blank=True)
    num_billing_cycle_failed = models.IntegerField(default=0, blank=True)

    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="recurring_payment_creator",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="recurring_payment_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='active', choices=STATUS_DETAIL_CHOICES)
    status = models.BooleanField(default=True)

    objects = RecurringPaymentManager()

    class Meta:
        app_label = 'recurring_payments'

    def __str__(self):
        return '%s - %s' % (self.user, self.description)

    def get_absolute_url(self):
        return reverse('recurring_payment.view_account', args=[self.id])

    def save(self, *args, **kwargs):
        self.guid = self.guid or str(uuid.uuid4())
        if self.taxable and self.tax_rate:
            self.tax_exempt = 0
        if not self.id:
            self.platform = get_setting("site", "global", "merchantaccount").lower()
        super(RecurringPayment, self).save(*args, **kwargs)

    @property
    def tax_rate_percentage(self):
        return '%.2f%s' % (float(self.tax_rate * 100), '%')

    @property
    def user_profile(self):
        """Insteading of using user.profile, this function traps the error.
        """
        try:
            profile = self.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create_profile(user=self.user)
        return profile

    @property
    def memberships(self):
        if self.object_content_type and self.object_content_type.name == 'Membership':
            return self.object_content_type.model_class().objects.filter(user=self.user,
                                                    auto_renew=True,
                                                    status=True,
                                                    status_detail__in=['active', 'expired']
                                             ).order_by('-expire_dt')
        return None

    def get_source_data(self):
        # https://www.pcisecuritystandards.org/pdfs/pci_fs_data_storage.pdf
        if self.platform == 'stripe':
            stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            stripe.api_version = settings.STRIPE_API_VERSION
            stripe_set_app_info(stripe)
            card = None
            if self.customer_profile_id:
                customer = stripe.Customer.retrieve(self.customer_profile_id)
                default_card_id = customer.get('default_card', None)
                if default_card_id:
                    card = customer.sources.retrieve(default_card_id)
                else:
                    default_source = customer.get('default_source', None)
                    if default_source:
                        sources = customer.get('sources', None)
                        if sources:
                            data = sources.get('data', None)
                            for c in data:
                                if c['id'] == default_source:
                                    card = c
                                    break
                if card:
                    return {'last4': card['last4'], 'exp_year': card['exp_year'], 'exp_month': card['exp_month']}
        return None

    def create_customer_profile_from_trans_id(self, trans_id):
        from tendenci.apps.recurring_payments.authnet.cim import CIMCustomerProfileFromTransaction
        cpt = CIMCustomerProfileFromTransaction()
        success, response_d = cpt.create(trans_id=trans_id)
        if success:
            self.customer_profile_id = response_d['customer_profile_id']
            self.save()
            customer_payment_profile_id = response_d['customer_payment_profile_id_list']['numeric_string']
            payment_profile = PaymentProfile(customer_profile_id=self.customer_profile_id,
                                             payment_profile_id=customer_payment_profile_id,
                                             creator=self.user,
                                             owner=self.user,
                                             creator_username= self.user.username,
                                             owner_username = self.user.username)
            payment_profile.save()

    def add_customer_profile(self):
        """Add the customer profile on payment gateway
        """
        if self.id and (not self.customer_profile_id):
            # check if this user already has a customer profile,
            # if so, no need to create a new one.
            cp_id_list = RecurringPayment.objects.filter(user=self.user).exclude(
                                customer_profile_id=''
                                ).values_list('customer_profile_id', flat=True)
            if cp_id_list:
                self.customer_profile_id  = cp_id_list[0]
                self.save()
            else:
                # create a customer profile on payment gateway
                cp = CIMCustomerProfile()
                d = {'email': self.user.email,
                     'customer_id': str(self.id)}
                success, response_d = cp.create(**d)
                print(success, response_d)
                if success:
                    self.customer_profile_id = response_d['customer_profile_id']
                    self.save()
                else:
                    if response_d["message_code"] == 'E00039':
                        p = re.compile(r'A duplicate record with ID (\d+) already exists.', re.I)
                        match = p.search(response_d['message_text'])
                        if match:
                            self.customer_profile_id  = match.group(1)
                            self.save()

    def delete_customer_profile(self):
        """Delete the customer profile on payment gateway
        """
        if self.customer_profile_id:
            has_other_rps = RecurringPayment.objects.filter(
                                        customer_profile_id=self.customer_profile_id
                                        ).exclude(id=self.id).exists()
            if not has_other_rps:
                cim_customer_profile = CIMCustomerProfile(self.customer_profile_id)
                cim_customer_profile.delete()

                # delete payment profile belonging to this recurring payment
                PaymentProfile.objects.filter(customer_profile_id=self.customer_profile_id).delete()
                return True
        return False

    def populate_payment_profile(self, *args, **kwargs):
        """
        Check payment gateway for the payment profiles for this customer
        and store the payment profile info locally

        Returns a list of valid and a list of invalid customer_payment_profile_ids

        Specifically,
             1) get a list of payment_profiles from gateway
             2) validate each one, if not valid, remove from the list
             3) if customer_payment_profile_id is not valid,
                delete it from database - keep only the valid ones on local.
        """
        valid_cim_payment_profile_ids = []
        invalid_cim_payment_profile_ids = []

        if not self.customer_profile_id:
            self.add_customer_profile()
            # return immediately -there is no payment profile yet
            return [], []

        validation_mode = kwargs.get('validation_mode')
        customer_profile = CIMCustomerProfile(self.customer_profile_id)
        success, response_d = customer_profile.get()

        if success:
            if 'payment_profiles' in response_d['profile']:
                # 1) get a list of payment_profiles from gateway
                cim_payment_profiles = response_d['profile']['payment_profiles']
                if not type(cim_payment_profiles) is list:
                    cim_payment_profiles = list([cim_payment_profiles])

                # 2) validate payment_profile, if not valid, remove it from the list
                if validation_mode:
                    for cim_payment_profile in cim_payment_profiles:
                        customer_payment_profile_id = cim_payment_profile['customer_payment_profile_id']
                        is_valid = False
                        # validate this payment profile
                        cpp = CIMCustomerPaymentProfile(self.customer_profile_id,
                                                        customer_payment_profile_id,
                                                        )
                        success, response_d  = cpp.validate(validation_mode=validation_mode)
                        # convert direct_response string into a dict
                        response_dict = direct_response_dict(response_d['direct_response'])
                        response_code = response_dict.get('response_code', '')
                        response_reason_code = response_dict.get('response_reason_code', '')

                        if all([success, response_code == '1', response_reason_code == '1']):
                            is_valid = True

                        if not is_valid:
                            invalid_cim_payment_profile_ids.append(cim_payment_profile['customer_payment_profile_id'])
                            # remove it from the list
                            cim_payment_profiles.remove(cim_payment_profile)
                        else:
                            valid_cim_payment_profile_ids.append(cim_payment_profile['customer_payment_profile_id'])

                list_cim_payment_profile_ids = [cim_payment_profile['customer_payment_profile_id']
                                                for cim_payment_profile in cim_payment_profiles]
                if not validation_mode:
                    valid_cim_payment_profile_ids.extend(list_cim_payment_profile_ids)

                # 3) if customer_payment_profile_id is not valid,
                #    delete it from database - keep only the valid ones on local
                payment_profiles = PaymentProfile.objects.filter(customer_profile_id=self.customer_profile_id)
                for pp in payment_profiles:
                    if pp.payment_profile_id not in list_cim_payment_profile_ids:
                        pp.delete()

                for cim_payment_profile in cim_payment_profiles:
                    customer_payment_profile_id = cim_payment_profile['customer_payment_profile_id']
                    # check if already exists, if not, insert to payment profiles table
                    payment_profiles = PaymentProfile.objects.filter(
                                payment_profile_id=customer_payment_profile_id)

                    if not payment_profiles:
                        payment_profile = PaymentProfile(customer_profile_id=self.customer_profile_id,
                                                         payment_profile_id=customer_payment_profile_id,
                                                         creator=self.user,
                                                         owner=self.user,
                                                         creator_username= self.user.username,
                                                         owner_username = self.user.username,
                                                         )
                        payment_profile.save()
                    else:
                        payment_profile = payment_profiles[0]

                    if 'credit_card' in cim_payment_profile['payment'] and \
                                'card_number' in cim_payment_profile['payment']['credit_card']:

                        card_num = cim_payment_profile['payment']['credit_card']['card_number'][-4:]
                        if payment_profile.card_num != card_num:
                            payment_profile.card_num = card_num
                            payment_profile.save()

        return valid_cim_payment_profile_ids, invalid_cim_payment_profile_ids

    def within_trial_period(self):
        now = datetime.now()

        # billing period has already started, skip the trial period.
        if now >= self.billing_start_dt:
            return False

        if all([self.has_trial_period, self.trial_period_start_dt]):
            if not self.trial_period_end_dt or self.trial_period_end_dt > self.billing_start_dt:
                self.trial_period_end_dt = self.billing_start_dt

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

        # the first billing
        if not last_billing_cycle:
            if self.within_trial_period():
                if not self.trial_period_end_dt or self.trial_period_end_dt > self.billing_start_dt:
                    self.trial_period_end_dt = self.billing_start_dt
                return (self.trial_period_start_dt, self.trial_period_end_dt)
            else:
                billing_cycle_start = self.billing_start_dt
                billing_cycle_end = billing_cycle_start + timedelta
        else:
            #billing_cycle_start = last_billing_cycle['end'] + relativedelta(days=1)
            billing_cycle_start = last_billing_cycle['end']

            billing_cycle_end = billing_cycle_start + timedelta

        return (billing_cycle_start, billing_cycle_end)

    def get_last_billing_cycle(self):
        rp_invs = RecurringPaymentInvoice.objects.filter(
                            recurring_payment=self).order_by('-billing_cycle_start_dt')
        if rp_invs:
            if self.has_trial_period and self.within_trial_period():
                return (rp_invs[0].billing_cycle_start_dt, rp_invs[0].billing_cycle_end_dt)

            if self.billing_start_dt <= rp_invs[0].billing_cycle_start_dt:
                return (rp_invs[0].billing_cycle_start_dt, rp_invs[0].billing_cycle_end_dt)
        return None

    def billing_cycle_t2d(self, billing_cycle):
        # convert tuple to dict
        if billing_cycle:
            billing_cycle = dict(zip(('start', 'end'), billing_cycle))
        return billing_cycle

    def get_payment_due_date(self, billing_cycle):
        """
        Get the payment due date for the billing cycle.
        """
        # num_days is the number days after billing cycle start/end date
        if self.due_sore == 'start':
            billing_dt = billing_cycle['start'] + relativedelta(days=self.num_days)
        else:
            billing_dt = billing_cycle['end'] + relativedelta(days=self.num_days)

        return billing_dt

    def check_and_generate_invoices(self, last_billing_cycle=None):
        """
        Check and generate invoices if needed.
        """
        now = datetime.now()

        if self.object_content_type and self.object_content_type.name == 'Membership':
            # check and renew for memberships with auto-renew enabled
            # that are expired or to be expired within 24 hours.
            memberships = self.memberships
            if memberships:
                for m in self.memberships:
                    if m.expire_dt < datetime(now.year, now.month, now.day, 0, 0, 0) + timedelta(days=1):
                        renewed_m = m.renew(m.user)
                        renewed_m.status_detail = 'pending'
                        renewed_m.save()
                        invoice = renewed_m.get_invoice()
                        rp_invoice = RecurringPaymentInvoice(
                                 recurring_payment=self,
                                 invoice=invoice,
                                 billing_dt=now)
                        rp_invoice.save()

        else:
            if not last_billing_cycle:
                last_billing_cycle = self.billing_cycle_t2d(self.get_last_billing_cycle())

            next_billing_cycle = self.billing_cycle_t2d(self.get_next_billing_cycle(last_billing_cycle))
            billing_dt = self.get_payment_due_date(next_billing_cycle)

            # determine when to create the invoice -
            # on the billing cycle start or end date
            if self.due_sore == 'start':
                invoice_create_dt = next_billing_cycle['start']
            else:
                invoice_create_dt = next_billing_cycle['end']

            if invoice_create_dt <= now:
                self.create_invoice(next_billing_cycle, billing_dt)
                # might need to notify admin and/or user that an invoice has been created.

                self.check_and_generate_invoices(next_billing_cycle)

    def create_invoice(self, billing_cycle, billing_dt):
        """
        Create an invoice and update the next_billing_dt for this recurring payment.
        """
        try:
            profile = self.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create_profile(user=self.user)

        if self.within_trial_period():
            amount = self.trial_amount
        else:
            amount = self.payment_amount

        self.next_billing_dt = billing_dt

        self.save()

        inv = Invoice()
        inv.due_date = billing_dt
        inv.ship_date = billing_dt

        inv.object_type = ContentType.objects.get(app_label=self._meta.app_label,
                                                  model=self._meta.model_name)
        inv.object_id = self.id
        inv.title = "Recurring Payment Invoice for Billing Cycle %s - %s" % (
                                           billing_cycle['start'].strftime('%m/%d/%Y'),
                                           billing_cycle['end'].strftime('%m/%d/%Y'))
        inv.bill_to_user(self.user)
        inv.status = True

        if self.taxable and self.tax_rate:
            inv.tax = self.tax_rate * amount
        else:
            inv.tax_exempt = 1
            inv.tax = 0

        inv.subtotal = amount
        inv.total = inv.subtotal + inv.tax

        inv.balance = inv.total
        inv.estimate = True
        inv.status_detail = 'estimate'

        inv.set_owner(self.user)

        inv.save(self.user)

        # tender the invoice
        inv.tender(self.user)

        rp_invoice = RecurringPaymentInvoice(
                             recurring_payment=self,
                             invoice=inv,
                             billing_cycle_start_dt=billing_cycle['start'],
                             billing_cycle_end_dt=billing_cycle['end'],
                             billing_dt=billing_dt

                                             )
        rp_invoice.save()

        return rp_invoice

    def get_current_balance(self):
        d = RecurringPaymentInvoice.objects.filter(
                                recurring_payment=self,
                                invoice__balance__gt=0,
                                billing_cycle_start_dt__lte=datetime.now(),
                                billing_cycle_end_dt__gte=datetime.now()
                                ).aggregate(current_balance=Sum('invoice__balance'))
        if not d['current_balance']:
            d['current_balance'] = 0
        return d['current_balance']

    def get_outstanding_balance(self):
        d = RecurringPaymentInvoice.objects.filter(
                                recurring_payment=self,
                                invoice__balance__gt=0,
                                billing_dt__lte=datetime.now()
                                ).aggregate(outstanding_balance=Sum('invoice__balance'))
        if not d['outstanding_balance']:
            d['outstanding_balance'] = 0
        return d['outstanding_balance']

    @property
    def total_paid(self):
        d = RecurringPaymentInvoice.objects.filter(
                                recurring_payment=self,
                                invoice__balance=0,
                                ).aggregate(total=Sum('invoice__total'))
        if not d['total']:
            d['total'] = 0
        return d['total']

    @property
    def total_unpaid(self):
        d = RecurringPaymentInvoice.objects.filter(
                                recurring_payment=self,
                                invoice__balance__gt=0,
                                ).aggregate(total=Sum('invoice__balance'))
        if not d['total']:
            d['total'] = 0
        return d['total']

class PaymentProfile(models.Model):
    #recurring_payment =  models.ForeignKey(RecurringPayment, on_delete=models.CASCADE)
    customer_profile_id = models.CharField(max_length=100)
    # assigned by gateway
    payment_profile_id = models.CharField(max_length=100, unique=True)
    card_type = models.CharField(max_length=50, null=True)
    # last 4 digits of card number
    card_num = models.CharField(max_length=4, null=True)
    expiration_dt = models.DateTimeField(blank=True, null=True)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="payment_profile_creator",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="payment_profile_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='active')
    status = models.BooleanField(default=True)

    class Meta:
        app_label = 'recurring_payments'

    def update_local(self, request):
        cim_payment_profile = CIMCustomerPaymentProfile(
                                self.recurring_payment.customer_profile_id,
                                self.payment_profile_id)
        success, response_d = cim_payment_profile.get()

        if success:
            if 'payment' in response_d['payment_profile']:
                if 'credit_card' in response_d['payment_profile']['payment'] and \
                        'card_number' in response_d['payment_profile']['payment']['credit_card']:
                    card_num = response_d['payment_profile']['payment']['credit_card']['card_number'][-4:]
                    self.card_num = card_num

        self.owner = request.user
        self.owner_username = request.user.username
        self.save()


class RecurringPaymentInvoice(models.Model):
    recurring_payment =  models.ForeignKey(RecurringPayment, related_name="rp_invoices", on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, blank=True, null=True, on_delete=models.CASCADE)
    billing_cycle_start_dt = models.DateTimeField(_("Billing cycle start date"), blank=True, null=True)
    billing_cycle_end_dt = models.DateTimeField(_('Billing cycle end date'), blank=True, null=True)
    last_payment_failed_dt = models.DateTimeField(_('Last payment failed date'), blank=True, null=True)
    # billing date is same as due date in invoice
    billing_dt = models.DateTimeField(blank=True, null=True)
    payment_received_dt = models.DateTimeField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    #is_paid = models.NullBooleanField(default=False)

    class Meta:
        app_label = 'recurring_payments'

    def make_payment_transaction(self, payment_profile_id, membership=None):
        """
        Make a payment transaction. This includes:
        1) Make an API call createCustomerProfileTransactionRequest
        2) Create a payment transaction entry
        3) Create a payment entry
        4) If the transaction is successful, populate payment entry with the direct response and mark payment as paid
        """
        amount = self.invoice.balance
        # tender the invoice
        self.invoice.tender(self.recurring_payment.user)

        # create a payment record
        payment = Payment()

        payment.payments_pop_by_invoice_user(self.recurring_payment.user,
                                             self.invoice,
                                             self.invoice.guid)

        if self.billing_cycle_start_dt and self.billing_cycle_end_dt:
            description = self.recurring_payment.description
            description += '(billing cycle from {0} to {1})'.format(
                            self.billing_cycle_start_dt.strftime('%m/%d/%Y'),
                            self.billing_cycle_end_dt.strftime('%m/%d/%Y'))
        else:
            description = payment.description

        # charge user
        if  self.recurring_payment.platform == "stripe":
            stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            stripe.api_version = settings.STRIPE_API_VERSION
            stripe_set_app_info(stripe)
            params = {
                       'amount': math.trunc(amount * 100), # amount in cents, again
                       'currency': get_setting('site', 'global', 'currency'),
                       'description': description,
                       'customer': self.recurring_payment.customer_profile_id
                      }

            success = False
            response_d = {
                          'status_detail': 'not approved',
                          'response_code': '0',
                          'response_reason_code': '0',
                          'result_code': 'Error',  # Error, Ok
                          'message_code': '',    # I00001, E00027
                          }
            try:
                charge_response = stripe.Charge.create(**params)
                success = True
                response_d['status_detail'] = 'approved'
                response_d['response_code'] = '1'
                response_d['response_subcode'] = '1'
                response_d['response_reason_code'] = '1'
                response_d['response_reason_text'] = 'This transaction has been approved. (Created# %s)' % charge_response.created
                response_d['trans_id'] = charge_response.id
                response_d['result_code'] = 'Ok'
                response_d['message_text'] = 'Successful.'
            except stripe.error.CardError as e:
                # it's a decline
                json_body = e.json_body
                err  = json_body and json_body['error']
                code = err and err['code']
                message = err and err['message']
                charge_response = '{message} status={status}, code={code}'.format(
                            message=message, status=e.http_status, code=code)

                response_d['response_reason_text'] = charge_response
                response_d['message_code'] = code
                response_d['message_text'] = charge_response
            except Exception as e:
                charge_response = e.message
                response_d['response_reason_text'] = charge_response
                response_d['message_text'] = charge_response[:200]

            # update payment
            for key in response_d:
                if hasattr(payment, key):
                    setattr(payment, key, response_d[key])

        else:
            # make a transaction using CIM
            d = {'amount': amount,
                 'order': {
                           'invoice_number': str(payment.invoice_num),
                           'description': description,
                           'recurring_billing': 'true'
                           }
                 }

            cpt = CIMCustomerProfileTransaction(self.recurring_payment.customer_profile_id,
                                                payment_profile_id)

            success, response_d = cpt.create(**d)

            # update the payment entry with the direct response returned from payment gateway
            payment = payment_update_from_response(payment, response_d['direct_response'])

        if success:
            payment.mark_as_paid()
            payment.save()
            payment.invoice.make_payment(self.recurring_payment.user, Decimal(payment.amount))
            # approve membership
            if membership:
                membership.approve()
                # send notification to user

            self.payment_received_dt = datetime.now()
        else:
            if payment.status_detail == '':
                payment.status_detail = 'not approved'
            payment.save()
            self.last_payment_failed_dt = datetime.now()

        self.save()

        # create a payment transaction record
        payment_transaction = PaymentTransaction(
                                    recurring_payment = self.recurring_payment,
                                    recurring_payment_invoice = self,
                                    payment_profile_id = payment_profile_id,
                                    trans_type='auth_capture',
                                    amount=amount,
                                    status=success)

        payment_transaction.payment = payment
        payment_transaction.result_code = response_d['result_code']
        payment_transaction.message_code = response_d['message_code']
        payment_transaction.message_text = response_d['message_text']

        payment_transaction.save()

        return payment_transaction

    def get_last_transaction_error_code(self):
        failed_trans = PaymentTransaction.objects.filter(recurring_payment_invoice=self,
                                                         status=False
                                                         ).order_by('-create_dt')
        if failed_trans:
            return failed_trans[0].message_code
        return None


class PaymentTransaction(models.Model):
    recurring_payment =  models.ForeignKey(RecurringPayment, related_name="transactions", on_delete=models.CASCADE)
    recurring_payment_invoice =  models.ForeignKey(RecurringPaymentInvoice, related_name="transactions", on_delete=models.CASCADE)
    payment_profile_id = models.CharField(max_length=100, default='')
    # trans_type - capture, refund or void
    trans_type  = models.CharField(max_length=50, null=True)
    # refid
    payment =  models.ForeignKey(Payment, null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    result_code = models.CharField(max_length=10, default='')
    message_code = models.CharField(max_length=20, default='')
    message_text = models.CharField(max_length=200, default='')

    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="payment_transaction_creator",  null=True, on_delete=models.SET_NULL)
    # True=success or False=failed
    status = models.BooleanField(default=True)
    #status_detail = models.CharField(max_length=50,  null=True)

    class Meta:
        app_label = 'recurring_payments'


def create_customer_profile(sender, instance=None, created=False, **kwargs):
    """ A post_save signal of RecurringPayment to create a customer profile
        on payment gateway.
    """
    if instance.id and instance.platform == 'authorizenet' and (not instance.customer_profile_id):
        # create a customer profile on payment gateway
        instance.add_customer_profile()

post_save.connect(create_customer_profile, sender=RecurringPayment)

def delete_customer_profile(sender, instance=None, user=None, **kwargs):
    """ A post_delete signal of RecurringPayment to delete a customer profile
        on payment gateway.
    """
    if instance.id and instance.platform == 'authorizenet' and instance.customer_profile_id:
        # create a customer profile on payment gateway
        instance.delete_customer_profile()

post_delete.connect(delete_customer_profile, sender=RecurringPayment)
