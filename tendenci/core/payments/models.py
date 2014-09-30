import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tendenci.apps.invoices.models import Invoice
from tendenci.core.site_settings.utils import get_setting


class Payment(models.Model):
    guid = models.CharField(max_length=50)
    invoice = models.ForeignKey(Invoice)
    payment_attempted = models.BooleanField(default=1)
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
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="payment_owner",
                              null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='')
    status = models.BooleanField(default=True)

    def save(self, user=None):
        if not self.id:
            self.guid = str(uuid.uuid1())
            if user and user.id:
                self.creator = user
                self.creator_username = user.username
        if user and user.id:
            self.owner = user
            self.owner_username = user.username

        super(Payment, self).save()

    @property
    def is_approved(self):
        return self.response_code == '1' and self.response_reason_code == '1'

    def mark_as_paid(self):
        self.status = True
        self.status_detail = 'approved'

    @property
    def is_paid(self):
        return all([self.response_code == '1',
                    self.response_reason_code == '1',
                    self.status_detail == 'approved'])

    def __unicode__(self):
        return u"response_code: %s, trans_id: %s, amount: %.2f" % (
                                       self.response_code,
                                       self.trans_id,
                                       self.amount)

    @models.permalink
    def get_absolute_url(self):
        return ('payment.view', [self.id, self.guid])

    def allow_view_by(self, user2_compare, guid=''):
        boo = False
        if user2_compare.profile.is_superuser:
            boo = True
        else:
            if user2_compare and user2_compare.id > 0:
                if self.creator == user2_compare or \
                    self.owner == user2_compare:
                    if self.status == 1:
                        boo = True
            else:
                # anonymous user
                if self.guid and self.guid == guid:
                    boo = True
        return boo

    def payments_pop_by_invoice_user(self, user, inv, session_id='', **kwargs):
        from django.core.urlresolvers import reverse
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

            # default description
            self.description = 'Tendenci Invoice %d Payment (%d).' % (
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
                        self.description = 'Tendenci Invoice %d for %s(%d).' % (
                                            inv.id, obj, inv.object_id)
                else:
                    self.description = 'Tendenci Invoice %d for %s(%d).' % (
                                            inv.id, obj, inv.object_id)

            # save the payment because we need the payment id below
            self.save(user)

            site_url = get_setting('site', 'global', 'siteurl')
            merchant_account = get_setting('site',
                                           "global",
                                           "merchantaccount").lower()
            if merchant_account == "authorizenet":
                self.response_page = reverse('authorizenet.sim_thank_you',
                                             args=[self.id])
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
                                             args=[self.id])
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
    is_online = models.BooleanField()
    admin_only = models.BooleanField(default=0,
                                     help_text=_(
                        "if checked, it will only show for administrators"))

    def __unicode__(self):
        name = "%s" % (self.human_name, )

        if self.is_online:
            return "%s - Online" % name
        return "%s - Offline" % name

