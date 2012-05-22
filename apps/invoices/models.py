import uuid
# guid = str(uuid.uuid1()) # based on the host ID and current time
#guid = str(uuid.uuid4())) # make a random UUID
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from perms.utils import is_admin, has_perm
from invoices.managers import InvoiceManager

from event_logs.models import EventLog

class Invoice(models.Model):
    guid = models.CharField(max_length=50)

    object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.IntegerField(default=0, blank=True, null=True)
    _object = generic.GenericForeignKey('object_type', 'object_id')

    title = models.CharField(max_length=150, blank=True, null=True)
    tender_date = models.DateTimeField(null=True)
    bill_to = models.CharField(max_length=120, blank=True)
    bill_to_first_name = models.CharField(max_length=100, blank=True, null=True)
    bill_to_last_name = models.CharField(max_length=100, blank=True, null=True)
    bill_to_company = models.CharField(max_length=50, blank=True, null=True)
    bill_to_address = models.CharField(max_length=100, blank=True, null=True)
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
    ship_to_company = models.CharField(max_length=50, blank=True)
    ship_to_address = models.CharField(max_length=100, blank=True)
    ship_to_city = models.CharField(max_length=50, blank=True)
    ship_to_state = models.CharField(max_length=50, blank=True)
    ship_to_zip_code = models.CharField(max_length=20, blank=True)
    ship_to_country = models.CharField(max_length=50, blank=True)
    ship_to_phone = models.CharField(max_length=50, blank=True, null=True)
    ship_to_fax = models.CharField(max_length=50, blank=True, null=True)
    ship_to_email = models.CharField(max_length=100, blank=True, null=True)
    ship_to_address_type = models.CharField(max_length=50, blank=True, null=True)
    receipt = models.BooleanField(default=0)
    gift = models.BooleanField(default=0)
    arrival_date_time = models.DateTimeField(blank=True, null=True)   
    greeting = models.CharField(max_length=500, blank=True, null=True)   
    instructions = models.CharField(max_length=500, blank=True, null=True)   
    po = models.CharField(max_length=50, blank=True)
    terms = models.CharField(max_length=50, blank=True)
    due_date = models.DateTimeField()
    ship_date = models.DateTimeField()
    ship_via = models.CharField(max_length=50, blank=True)
    fob = models.CharField(max_length=50, blank=True, null=True)
    project = models.CharField(max_length=50, blank=True, null=True)   
    other = models.CharField(max_length=120, blank=True, null=True)
    message = models.CharField(max_length=150, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    shipping = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipping_surcharge =models.DecimalField(max_digits=6, decimal_places=2, default=0)
    box_and_packing = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    tax_exempt =models.BooleanField(default=1)
    tax_exemptid = models.CharField(max_length=50, blank=True, null=True)  
    tax_rate = models.FloatField(blank=True, default=0)
    taxable = models.BooleanField(default=0)
    tax = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    variance = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    payments_credits = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    estimate = models.BooleanField(default=1)
    disclaimer = models.CharField(max_length=150, blank=True, null=True)
    variance_notes = models.TextField(max_length=1000, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="invoice_creator",  null=True)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="invoice_owner", null=True)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='estimate')
    status = models.BooleanField(default=True)
    
    objects = InvoiceManager()
    
    class Meta:
        permissions = (("view_invoice","Can view invoice"),)
    
    def __unicode__(self):
        return u'%s' % (self.title)
    
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
        from accountings.utils import make_acct_entries
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
        if is_admin(user2_compare):
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
        from accountings.utils import make_acct_entries
        if self.is_tendered:
            self.balance -= amount
            self.payments_credits += amount
            self.save()
            
            # Make the accounting entries here
            make_acct_entries(user, self, amount)
        
        
        