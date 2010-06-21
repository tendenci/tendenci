import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from perms.utils import is_admin

class MakePayment(models.Model):
    guid = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    company = models.CharField(max_length=50, default='', blank=True, null=True)
    address = models.CharField(max_length=100, default='', blank=True, null=True)
    address2 = models.CharField(_('address line 2'), max_length=100, default='', blank=True, null=True)
    city = models.CharField(max_length=50, default='', blank=True, null=True)
    state = models.CharField(max_length=50, default='', blank=True, null=True)
    zip_code = models.CharField(max_length=50, default='', blank=True, null=True)
    country = models.CharField(max_length=50, default='', blank=True, null=True)
    email = models.CharField(max_length=50, default='',  null=True)
    phone = models.CharField(max_length=50, default='', blank=True, null=True)
    referral_source = models.CharField(_('referred by'), max_length=200, default='', blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_count = models.IntegerField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='cc')
    invoice_id = models.IntegerField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True,  related_name="make_payment_creator")
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, null=True, related_name="make_payment_owner")
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='estimate')
    status = models.BooleanField(default=True)
    
    def save(self, user=None):
        if not self.id:
            self.guid = str(uuid.uuid1())
            if user and user.id:
                self.creator=user
                self.creator_username=user.username
        if user and user.id:
            self.owner=user
            self.owner_username=user.username
            
        super(self.__class__, self).save()
        
    def allow_view_by(self, user2_compare):
        boo = False
        if is_admin(user2_compare):
            boo = True
        else: 
            if user2_compare and user2_compare.id > 0:
                if self.creator == user2_compare or self.owner == user2_compare:
                    if self.status == 1:
                        boo = True
            
        return boo
    