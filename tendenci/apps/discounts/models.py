from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.discounts.managers import DiscountManager

class Discount(TendenciBaseModel):
    discount_code = models.CharField(max_length=100, unique=True, help_text=_('Discount codes must be unique.'))
    start_dt = models.DateTimeField(_('Start Date/Time'))
    end_dt = models.DateTimeField(_('Start Date/Time'))
    apps = models.ManyToManyField(ContentType, verbose_name=_('Applications'), help_text=_('Select the applications that can use this discount.'))
    never_expires = models.BooleanField(_('Never Expires'), help_text=_('Check this box to make the discount code never expire.'), default=False)
    value = models.DecimalField(_('Discount Value'), max_digits=10, decimal_places=2, help_text=_('Enter discount value as a positive number.'))
    cap = models.IntegerField(_('Maximum Uses'), help_text=_('Enter 0 for unlimited discount code uses.'), default=0)

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = DiscountManager()

    class Meta:
        permissions = (("view_discount",_("Can view discount")),)
        app_label = 'discounts'

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

    @staticmethod
    def has_valid_discount(**kwargs):
        now = datetime.now()
        model = kwargs.pop('model', None)
        discount_exists = Discount.objects.filter(
                            Q(never_expires=True) |
                            Q(start_dt__lt=now,
                            end_dt__gte=now)
                            ).filter(apps__model=model).exists()
        return discount_exists

class DiscountUse(models.Model):
    invoice = models.ForeignKey(Invoice)
    discount = models.ForeignKey(Discount)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'discounts'

    def __unicode__(self):
        return "%s:%s" % (self.invoice, self.discount)
