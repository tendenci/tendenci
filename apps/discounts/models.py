from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from perms.models import TendenciBaseModel
from perms.object_perms import ObjectPermission
from invoices.models import Invoice
from discounts.managers import DiscountManager

class Discount(TendenciBaseModel):
    class Meta:
        permissions = (("view_discount","Can view discount"),)
        
    discount_code = models.CharField(max_length=100, unique=True, help_text=_('Discount codes must be unique.'))
    start_dt = models.DateTimeField(_('Start Date/Time'))
    end_dt = models.DateTimeField(_('Start Date/Time'))
    never_expires = models.BooleanField(_('Never Expires'), help_text=_('Check this box to make the discount code never expire.'))
    value = models.DecimalField(_('Discount Value'), max_digits=10, decimal_places=2, help_text=_('Enter discount value as a positive number.'))
    cap = models.IntegerField(_('Maximum Uses'), help_text=_('Enter 0 for unlimited discount code uses.'))

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = DiscountManager()
    
    def num_of_uses(self):
        return self.discountuse_set.count()
    
    def available(self):
        """
        Determines if this discount has is still usable based on its
        cap.
        """
        if self.num_of_uses() > self.cap and self.cap != 0:
            return False
        if datetime.now() > self.end_dt and not self.never_expires:
            return False
        return True
        
    def available_for(self, count):
        """
        Determines if count number of uses is still available.
        """
        if (self.num_of_uses() + count) > self.cap and self.cap != 0:
            return False
        if datetime.now() > self.end_dt and not self.never_expires:
            return False
        return True
    
    def __unicode__(self):
        return self.discount_code
        
    @models.permalink
    def get_absolute_url(self):
        return('discount.detail', [self.pk])
    
class DiscountUse(models.Model):
    invoice = models.ForeignKey(Invoice)
    discount = models.ForeignKey(Discount)
    create_dt = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s:%s" % (self.invoice, self.discount)
