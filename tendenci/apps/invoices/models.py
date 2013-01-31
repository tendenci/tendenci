import uuid
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from tendenci.core.perms.utils import has_perm
from tendenci.apps.invoices.managers import InvoiceManager
from tendenci.core.event_logs.models import EventLog


class Invoice(models.Model):
    guid = models.CharField(max_length=50)

    object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.IntegerField(default=0, blank=True, null=True)
    _object = generic.GenericForeignKey('object_type', 'object_id')

    title = models.CharField(max_length=150, blank=True, null=True)
    #user
    creator = models.ForeignKey(User, related_name="invoice_creator",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="invoice_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    #dates
    create_dt = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    update_dt = models.DateTimeField(auto_now=True)
    tender_date = models.DateTimeField(null=True)
    arrival_date_time = models.DateTimeField(blank=True, null=True)
    #payment status
    status_detail = models.CharField(max_length=50, default='estimate')
    status = models.BooleanField(default=True)
    estimate = models.BooleanField(default=1)
    payments_credits = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    #other
    variance = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    variance_notes = models.TextField(max_length=1000, blank=True, null=True)
    receipt = models.BooleanField(default=0)
    gift = models.BooleanField(default=0)
    greeting = models.CharField(max_length=500, blank=True, null=True)
    instructions = models.CharField(max_length=500, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True)
    terms = models.CharField(max_length=50, blank=True)
    disclaimer = models.CharField(max_length=150, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    fob = models.CharField(max_length=50, blank=True, null=True)
    project = models.CharField(max_length=50, blank=True, null=True)
    other = models.CharField(max_length=120, blank=True, null=True)
    message = models.CharField(max_length=150, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    tax_exempt = models.BooleanField(default=1)
    tax_exemptid = models.CharField(max_length=50, blank=True, null=True)
    tax_rate = models.FloatField(blank=True, default=0)
    taxable = models.BooleanField(default=0)
    tax = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    #bill/ ship
    bill_to = models.CharField(max_length=120, blank=True)
    bill_to_first_name = models.CharField(max_length=100, blank=True, null=True)
    bill_to_last_name = models.CharField(max_length=100, blank=True, null=True)
    bill_to_company = models.CharField(max_length=100, blank=True, null=True)
    bill_to_address = models.CharField(max_length=250, blank=True, null=True)
    bill_to_city = models.CharField(max_length=50, blank=True, null=True)
    bill_to_state = models.CharField(max_length=50, blank=True, null=True)
    bill_to_zip_code = models.CharField(max_length=20, blank=True, null=True)
    bill_to_country = models.CharField(max_length=50, blank=True, null=True)
    bill_to_phone = models.CharField(max_length=50, blank=True, null=True)
    bill_to_fax = models.CharField(max_length=50, blank=True, null=True)
    bill_to_email = models.CharField(max_length=100, blank=True, null=True)
    ship_to = models.CharField(max_length=120, blank=True)
    ship_to_first_name = models.CharField(max_length=50, blank=True)
    ship_to_last_name = models.CharField(max_length=50, blank=True)
    ship_to_company = models.CharField(max_length=100, blank=True)
    ship_to_address = models.CharField(max_length=250, blank=True)
    ship_to_city = models.CharField(max_length=50, blank=True)
    ship_to_state = models.CharField(max_length=50, blank=True)
    ship_to_zip_code = models.CharField(max_length=20, blank=True)
    ship_to_country = models.CharField(max_length=50, blank=True)
    ship_to_phone = models.CharField(max_length=50, blank=True, null=True)
    ship_to_fax = models.CharField(max_length=50, blank=True, null=True)
    ship_to_email = models.CharField(max_length=100, blank=True, null=True)
    ship_to_address_type = models.CharField(max_length=50, blank=True, null=True)
    ship_date = models.DateTimeField()
    ship_via = models.CharField(max_length=50, blank=True)
    shipping = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipping_surcharge = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    box_and_packing = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    objects = InvoiceManager()

    class Meta:
        permissions = (("view_invoice", "Can view invoice"), )

    # def __unicode__(self):
    #     return u'%s' % (self.title)

    def set_creator(self, user):
        self.creator = user
        self.creator_username = user.username

    def set_owner(self, user):
        self.owner = user
        self.owner_username = user.username

    def bill_to_user(self, user):
        """
        This method populates all of the ship to fields
        via info in user and user.profile object.
        """
        self.bill_to = '%s %s' % (user.first_name, user.last_name)
        self.bill_to = self.bill_to.strip()

        self.bill_to_first_name = user.first_name
        self.bill_to_last_name = user.last_name
        self.bill_to_company = user.profile.company
        self.bill_to_address = user.profile.address
        self.bill_to_city = user.profile.city
        self.bill_to_state = user.profile.state
        self.bill_to_zip_code = user.profile.zipcode
        self.bill_to_country = user.profile.country
        self.bill_to_phone = user.profile.phone
        self.bill_to_fax = user.profile.fax
        self.bill_to_email = user.email

    def ship_to_user(self, user):
        """
        This method populates all of the ship to fields
        via info in user and user.profile object.
        """
        self.bill_to = '%s %s' % (user.first_name, user.last_name)
        self.ship_to = self.ship_to.strip()

        self.ship_to_first_name = user.first_name
        self.ship_to_last_name = user.last_name
        self.ship_to_company = user.profile.company
        self.ship_to_address = user.profile.address
        self.ship_to_city = user.profile.city
        self.ship_to_state = user.profile.state
        self.ship_to_zip_code = user.profile.zipcode
        self.ship_to_country = user.profile.country
        self.ship_to_phone = user.profile.phone
        self.ship_to_fax = user.profile.fax
        self.ship_to_email = user.email
        self.ship_to_address_type = user.profile.address_type

    def split_title(self):
        if ": " in self.title:
            split_title = ': '.join(self.title.split(': ')[1:])
            return u'%s' % split_title
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('invoice.view', [self.id])
    
    def save(self, user=None):
        if not self.id:
            self.guid = str(uuid.uuid1())
            if user and user.id:
                self.creator=user
                self.creator_username=user.username
        if user and user.id:
            self.owner=user
            self.owner_username=user.username
            
        super(Invoice, self).save()
        
    def get_object(self):
        _object = None
        try:
            _object = self._object
        except:
            pass
        return _object
    
    @property
    def is_tendered(self):
        boo = False
        if self.id > 0:
            if self.status_detail.lower() == 'tendered':
                boo = True
        return boo
    
    def tender(self, user):
        from tendenci.apps.accountings.utils import make_acct_entries
        """ mark it as tendered if we have records """ 
        if not self.is_tendered:
            # make accounting entry
            make_acct_entries(user, self, self.total)
            
            self.estimate = False
            self.status_detail = 'tendered'
            self.status = 1
            self.tender_date = datetime.now()
            self.save()
        return True
            
    
    # if this invoice allows view by user2_compare
    def allow_view_by(self, user2_compare, guid=''):
        if user2_compare.profile.is_superuser:
            return True
        
        if has_perm(user2_compare, 'invoices.view_invoice'):
            return True

        if self.guid == guid:
            return True

        if user2_compare.is_authenticated():
            if user2_compare in [self.creator, self.owner]:
                return self.status

        return False

    def allow_payment_by(self, user2_compare,  guid=''):
        return self.allow_view_by(user2_compare,  guid)
    
    # if this invoice allows edit by user2_compare
    def allow_edit_by(self, user2_compare, guid=''):
        boo = False
        if user2_compare.is_superuser:
            boo = True
        else:
            if user2_compare and user2_compare.id > 0: 
                if has_perm(user2_compare, 'invoices.change_invoice'):
                    return True
        
                if self.creator == user2_compare or self.owner == user2_compare:
                    if self.status == 1:
                        # user can only edit a non-tendered invoice
                        if not self.is_tendered:
                            boo = True
            else:
                if self.guid and self.guid == guid: # for anonymous user
                    if self.status == 1 and not self.is_tendered:  
                        boo = True
        return boo
        
     
    # this function is to make accounting entries    
    def make_payment(self, user, amount):
        from tendenci.apps.accountings.utils import make_acct_entries
        if self.is_tendered:
            self.balance -= amount
            self.payments_credits += amount
            self.save()
            
            # Make the accounting entries here
            make_acct_entries(user, self, amount)

    def void_payment(self, user, amount):
        self.balance += amount
        self.payments_credits -= amount
        self.save()
        for payment in self.payment_set.all():
            payment.status_detail = 'void'
            payment.save()
