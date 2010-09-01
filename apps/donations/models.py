import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from invoices.models import Invoice
from donations.managers import DonationManager

class Donation(models.Model):
    guid = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=True)
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
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True,  related_name="donation_creator")
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, null=True, related_name="donation_owner")
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='estimate')
    status = models.BooleanField(default=True)
    
    objects = DonationManager()
    
    def save(self, user=None, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            if user and user.id:
                self.creator=user
                self.creator_username=user.username
        if user and user.id:
            self.owner=user
            self.owner_username=user.username
            
        super(self.__class__, self).save(*args, **kwargs)
