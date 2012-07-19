from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from perms.indexes import TendenciBaseSearchIndex
from perms.object_perms import ObjectPermission
from discounts.models import Discount

class DiscountIndex(TendenciBaseSearchIndex):
    discount_code = indexes.CharField(model_attr='discount_code')
    start_dt = indexes.DateTimeField(model_attr='start_dt')
    end_dt = indexes.DateTimeField(model_attr='end_dt')
    never_expires = indexes.BooleanField(model_attr='never_expires')
    value = indexes.DecimalField(model_attr='value')
    cap = indexes.IntegerField(model_attr='cap')
    
    num_of_uses = indexes.IntegerField()
    
    def prepare_num_of_uses(self, obj):
        return obj.num_of_uses()

site.register(Discount, DiscountIndex)
