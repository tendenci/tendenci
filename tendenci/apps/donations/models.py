import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.donations.managers import DonationManager

class Donation(models.Model):
    guid = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=50, default='', blank=True, null=True)
    address = models.CharField(max_length=100, default='', blank=True, null=True)
    address2 = models.CharField(_('address line 2'), max_length=100, default='', blank=True, null=True)
    city = models.CharField(max_length=50, default='', blank=True, null=True)
    state = models.CharField(max_length=50, default='', blank=True, null=True)
    zip_code = models.CharField(max_length=50, default='', blank=True, null=True)
    country = models.CharField(max_length=50, default='', blank=True, null=True)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    referral_source = models.CharField(_('referred by'), max_length=200, default='', blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2)
    allocation = models.CharField(max_length=150, default='', blank=True,  null=True)
    payment_method = models.CharField(max_length=50, default='cc')
    invoice = models.ForeignKey(Invoice, blank=True, null=True, on_delete=models.SET_NULL)
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True,  related_name="donation_creator", on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=150, null=True)
    owner = models.ForeignKey(User, null=True, related_name="donation_owner", on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=150, null=True)
    status_detail = models.CharField(max_length=50, default='estimate')
    status = models.NullBooleanField(default=True)

    objects = DonationManager()

    class Meta:
        app_label = 'donations'
        verbose_name = _("Donation")
        verbose_name_plural = _("Donations")

    def save(self, user=None, *args, **kwargs):
        for field in self._meta.fields:
            # avoid saving as null for the string-based fields
            field_name = field.name
            if getattr(self, field_name) is None and field.null and field.get_internal_type() in ['CharField', 'CharField']:
                setattr(self,field_name, field.get_default())
            
        if not self.id:
            self.guid = str(uuid.uuid4())
            if user and user.id:
                self.creator=user
                self.creator_username=user.username
        if user and user.id:
            self.owner=user
            self.owner_username=user.username

        super(Donation, self).save(*args, **kwargs)

    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        """
        return 'Tendenci Invoice %d Payment for Donation %d' % (
            inv.id,
            inv.object_id,
        )

    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the donation sale
        """
        from tendenci.apps.accountings.models import Acct, AcctEntry, AcctTran
        from tendenci.apps.accountings.utils import make_acct_entries_initial, make_acct_entries_closing

        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)

            # #CREDIT donation SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount*(-1))

    def get_acct_number(self, discount=False):
        if discount:
            return 465100
        else:
            return 405100

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """
        # email to admin
        try:
            from tendenci.apps.notifications import models as notification
        except:
            notification = None
        from tendenci.apps.perms.utils import get_notice_recipients

        recipients = get_notice_recipients('module', 'donations', 'donationsrecipients')
        if recipients:
            if notification:
                extra_context = {
                    'donation': self,
                    'invoice': payment.invoice,
                    'request': request,
                }
                notification.send_emails(recipients,'donation_added', extra_context)
