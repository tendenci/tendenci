from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Manager

class InvoiceManager(Manager):
    def create_invoice(self, user, **kwargs):
        return self.create(title=kwargs.get('title', ''), 
                           estimate=kwargs.get('estimate', True),
                           status=kwargs.get('status', True), 
                           status_detail=kwargs.get('status_detail', 'estimate'),
                           invoice_object_type=kwargs.get('invoice_object_type', ''),
                           invoice_object_type_id=kwargs.get('invoice_object_type_id', 0),
                           subtotal=kwargs.get('subtotal', 0),
                           total=kwargs.get('total', 0),
                           balance=kwargs.get('balance', 0),
                           creator_id=user.id, 
                           creator_username=user.username,
                           owner_id=user.id, 
                           owner_username=user.username)

class Invoice(models.Model):
    guid = models.CharField(max_length=50)
    invoice_object_type = models.CharField(_('object_type'), max_length=50, blank=True, null=True)
    invoice_object_type_id = models.IntegerField(blank=True, null=True)
    job_id = models.IntegerField(null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    tender_date = models.DateTimeField(null=True)
    # priceasofdate and invoice_number seem like not being used in T4
    #priceasofdate = models.DateTimeField(null=True)
    #invoice_number = models.IntegerField(null=True)
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
    receip= models.BooleanField(default=0)
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
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    shipping = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    shipping_surcharge =models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    box_and_packing = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tax_exempt =models.BooleanField(default=1)
    tax_exemptid = models.CharField(max_length=50, blank=True, null=True)  
    tax_rate = models.FloatField(blank=True, default=0)
    taxable = models.BooleanField(default=0)
    tax = models.DecimalField(max_digits=6, decimal_places=4, blank=True)
    variance = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    payments_credits = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    estimate = models.BooleanField(default=1)
    disclaimer = models.CharField(max_length=150, blank=True, null=True)
    variance_notes = models.CharField(max_length=1000, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="invoices_creator",  null=True)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="invoices_owner", null=True)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='estimate')
    status = models.BooleanField(default=True)
    
    objects = InvoiceManager()
