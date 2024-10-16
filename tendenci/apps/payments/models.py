import uuid

import stripe

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.payments.stripe.utils import stripe_set_app_info
from tendenci.apps.site_settings.utils import get_setting


class PaymentQuerySet(models.QuerySet):
    def stripe(self):
        """Filter payments with a Stripe transaction ID"""
        merchant_account = get_setting("site", "global", "merchantaccount").lower()
        if merchant_account != 'stripe':
            return self.none()

        return self.exclude(trans_id='')

    def refundable(self):
        """Filter Stripe payments with a remaining refundable amount"""
        return self.stripe().filter(refundable_amount__gt=0, status_detail='approved')


class PaymentManager(models.Manager.from_queryset(PaymentQuerySet)):
    pass


class Payment(models.Model):
    guid = models.CharField(max_length=50)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment_attempted = models.BooleanField(default=True)
    check_number = models.CharField(max_length=10, default='', blank=True)
    response_code = models.CharField(max_length=2, default='')
    response_subcode = models.CharField(max_length=10, default='')
    response_reason_code = models.CharField(max_length=15, default='')
    response_reason_text = models.TextField(default='')
    response_page = models.CharField(max_length=200)
    trans_id = models.CharField(max_length=100, default='')
    trans_string = models.CharField(max_length=100)
    card_type = models.CharField(max_length=50, default='', null=True)
    # the last 4 digits of credit card
    account_number = models.CharField(max_length=4, default='', null=True)
    po_num = models.CharField(max_length=50, blank=True)
    auth_code = models.CharField(max_length=10)
    avs_code = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    refundable_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    invoice_num = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=1600)
    first_name = models.CharField(max_length=100, default='',
                                  blank=True, null=True)
    last_name = models.CharField(max_length=100, default='',
                                 blank=True, null=True)
    company = models.CharField(max_length=100, default='',
                               blank=True, null=True)
    address = models.CharField(max_length=250, default='',
                               blank=True, null=True)
    address2 = models.CharField(max_length=100, default='',
                                blank=True, null=True)
    city = models.CharField(max_length=50, default='',
                            blank=True, null=True)
    state = models.CharField(max_length=50, default='',
                             blank=True, null=True)
    zip = models.CharField(max_length=20, default='',
                           blank=True, null=True)
    country = models.CharField(max_length=60, default='',
                               blank=True, null=True)
    phone = models.CharField(max_length=50, default='',
                             blank=True, null=True)
    fax = models.CharField(max_length=50, default='',
                           blank=True, null=True)
    email = models.CharField(max_length=255, default='',
                             blank=True, null=True)
    ship_to_first_name = models.CharField(max_length=100,
                                          default='', null=True)
    ship_to_last_name = models.CharField(max_length=100,
                                         default='', null=True)
    ship_to_company = models.CharField(max_length=100,
                                       default='', null=True)
    ship_to_address = models.CharField(max_length=250,
                                       default='', null=True)
    ship_to_city = models.CharField(max_length=50,
                                    default='', null=True)
    ship_to_state = models.CharField(max_length=50, default='', null=True)
    ship_to_zip = models.CharField(max_length=20, default='', null=True)
    ship_to_country = models.CharField(max_length=60, default='', null=True)
    method = models.CharField(max_length=50)
    freight = models.CharField(max_length=16, blank=True)
    tax_exempt = models.CharField(max_length=16, blank=True)
    md5_hash = models.CharField(max_length=255)
    payment_type = models.CharField(max_length=20)
    cust_id = models.CharField(max_length=20, default=0)
    tax = models.CharField(max_length=16, blank=True)
    duty = models.CharField(max_length=16, blank=True)
    verified = models.BooleanField(blank=True, default=False)
    submit_dt = models.DateTimeField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="payment_creator",
                                null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=150, null=True)
    owner = models.ForeignKey(User, related_name="payment_owner",
                              null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=150, null=True)
    status_detail = models.CharField(max_length=50, default='')
    status = models.BooleanField(default=True)

    objects = PaymentManager()

    class Meta:
        app_label = 'payments'

    def save(self, user=None, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())
            if user and user.id:
                self.creator = user
                self.creator_username = user.username
        if user and user.id:
            self.owner = user
            self.owner_username = user.username

        super(Payment, self).save(*args, **kwargs)

    @property
    def completed_refunds(self):
        """All completed refunds associated with this payment"""
        return self.refund_set.filter(response_status=Refund.Status.SUCCEEDED)

    @property
    def is_approved(self):
        return self.response_code == '1' and self.response_reason_code == '1'

    def mark_as_paid(self):
        self.status = True
        self.status_detail = 'approved'
        self.refundable_amount = self.amount

    def refund(self, amount=None, notes=None):
        """Refund full or partial amount of Payment through Stripe"""
        merchant_account = get_setting("site", "global", "merchantaccount").lower()

        if not self.trans_id or merchant_account != 'stripe':
            raise Exception(_("Refund requires a Stripe transaction ID"))

        refundable_amount = amount or self.amount
        Refund.objects.create(
            invoice=self.invoice,
            payment=self,
            trans_id=self.trans_id,
            amount=refundable_amount,
            notes=notes,
        )

        self.refundable_amount -= refundable_amount
        self.save(update_fields=['refundable_amount'])

    @property
    def is_paid(self):
        return all([self.response_code == '1',
                    self.response_reason_code == '1',
                    self.status_detail == 'approved'])

    def __str__(self):
        return "response_code: %s, trans_id: %s, amount: %.2f" % (
                                       self.response_code,
                                       self.trans_id,
                                       self.amount)

    def get_absolute_url(self):
        return reverse('payment.view', args=[self.id, self.guid])

    def allow_view_by(self, user2_compare, guid=''):
        if user2_compare.profile.is_superuser:
            return True

        if not user2_compare.is_anonymous:
            if self.creator == user2_compare or \
                self.owner == user2_compare:
                return self.status

        return False

    def payments_pop_by_invoice_user(self, user, inv, session_id='', **kwargs):
        boo = False
        if inv.allow_payment_by(user, session_id):
            boo = True
            self.first_name = inv.bill_to_first_name
            self.last_name = inv.bill_to_last_name
            self.company = inv.bill_to_company
            self.phone = inv.bill_to_phone
            self.email = inv.bill_to_email
            if user and user.id:
                self.cust_id = user.id
            self.address = inv.bill_to_address
            self.city = inv.bill_to_city
            self.state = inv.bill_to_state
            self.zip = inv.bill_to_zip_code
            self.country = inv.bill_to_country

            self.fax = inv.bill_to_fax
            self.ship_to_first_name = inv.ship_to_first_name
            self.ship_to_last_name = inv.ship_to_last_name
            self.ship_to_company = inv.ship_to_company
            self.ship_to_address = inv.ship_to_address
            self.ship_to_city = inv.ship_to_city
            self.ship_to_state = inv.ship_to_state
            self.ship_to_zip = inv.ship_to_zip_code
            self.ship_to_country = inv.ship_to_country
            self.amount = inv.balance
            self.invoice = inv
            # hard coded here - same as in T4
            self.method = 'cc'
            self.status = True
            self.check_number = ''

            # default description
            self.description = 'Invoice %d Payment (%d).' % (
                                                              inv.id,
                                                              inv.object_id)

            # override description
            obj = inv.get_object()
            if obj:
                if hasattr(obj, 'get_payment_description'):
                    description = obj.get_payment_description(inv)
                    if description:
                        self.description = description
                    else:
                        self.description = 'Invoice %d for %s(%d).' % (
                                            inv.id, obj, inv.object_id)
                else:
                    self.description = 'Invoice %d for %s(%d).' % (
                                            inv.id, obj, inv.object_id)

            # save the payment because we need the payment id below
            self.save(user)

            site_url = get_setting('site', 'global', 'siteurl')
            merchant_account = get_setting('site',
                                           "global",
                                           "merchantaccount").lower()
            if merchant_account == "authorizenet":
                self.response_page = ''
            elif merchant_account == "firstdata":
                self.response_page = reverse('firstdata.thank_you',
                                             args=[self.id])
            elif merchant_account == "firstdatae4":
                self.response_page = reverse('firstdatae4.thank_you')
            elif merchant_account == "paypalpayflowlink":
                self.response_page = reverse('payflowlink.thank_you')
            elif merchant_account == "paypal":
                self.response_page = reverse('paypal.thank_you')
            elif merchant_account == "stripe":
                self.response_page = reverse('stripe.thank_you',
                                             args=[self.id, self.guid])
            else:
                self.response_page = "/payments/thankyou/%d" % (self.id)

            self.response_page = '%s%s' % (site_url, self.response_page)

            self.invoice_num = self.id
            self.save()

        return boo


class PaymentMethod(models.Model):
    """
        Manage payment methods with this object.
        The payment methods chosen will affect the entire website.
    """
    human_name = models.CharField(max_length=200, blank=False)
    machine_name = models.CharField(max_length=200, blank=False)
    is_online = models.BooleanField(default=False)
    admin_only = models.BooleanField(default=False,
                                     help_text=_(
                        "if checked, it will only show for administrators"))

    class Meta:
        app_label = 'payments'

    def __str__(self):
        name = "%s" % (self.human_name, )

        if self.is_online:
            return "%s - Online" % name
        return "%s - Offline" % name


class RefundQuerySet(models.QuerySet):
    def connect_to_stripe(self):
        """Make sure Stripe has the API Key"""
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        stripe.api_version = settings.STRIPE_API_VERSION
        stripe_set_app_info(stripe)

    def create(self, *args, **kwargs):
        """Refund through Stripe and save record of transaction"""
        instance = super().create(*args, **kwargs)
        try:
            amount_in_cents = int(instance.amount * 100)
            params = {'charge': instance.trans_id, 'amount': amount_in_cents}
            stripe_connected_account, scope = instance.invoice.stripe_connected_account()

            if stripe_connected_account:
                
                if scope == "express":
                    params.update({'refund_application_fee':True})
                    params.update({'reverse_transfer':True})
                else:
                    # stripe_account only needs to be specified for standard account,
                    # not for express account 
                    params.update({'stripe_account': stripe_connected_account})

            self.connect_to_stripe()
            response = stripe.Refund.create(**params)
            instance.update_stripe(response)
        except Exception as e:
            instance.response_status = Refund.Status.FAILED
            instance.error_message = e
            instance.save(update_fields=['error_message', 'response_status'])
            raise


class RefundManager(models.Manager.from_queryset(RefundQuerySet)):
    pass


class Refund(models.Model):
    """
    Track refunds made through Stripe.
    Refunds will always have a corresponding Payment and Invoice.
    trans_id is the Stripe charge ID of the related Payment.
    """
    class Status:
        PENDING = 'pending'
        SUCCEEDED = 'succeeded'
        FAILED = 'failed'

        CHOICES = (
            (PENDING, _('Pending')),
            (SUCCEEDED, _('Succeeded')),
            (FAILED, _('Failed'))
        )

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    response_status = models.CharField(
        max_length=50, default=Status.PENDING, choices=Status.CHOICES)
    response_reason_text = models.TextField(default='')
    error_message = models.TextField(blank=True, null=True)
    trans_id = models.CharField(max_length=100)
    refund_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_dt = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    objects = RefundManager()

    def update_stripe(self, refund_response):
        """Update to reflect Stripe refund response"""
        if hasattr(refund_response, 'id'):
            self.refund_id = refund_response.id

        if hasattr(refund_response, 'status') and refund_response.status == 'succeeded':
            self.response_status = self.Status.SUCCEEDED
            self.response_reason_text = 'Refund successfully processed.'
        else:
            self.response_status = self.Status.FAILED
            self.response_reason_text = refund_response

        self.save()

    @property
    def net_amount(self):
        return self.amount * -1
