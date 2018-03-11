from haystack import indexes

from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.discounts.models import Discount

class DiscountIndex(TendenciBaseSearchIndex, indexes.Indexable):
    discount_code = indexes.CharField(model_attr='discount_code')
    start_dt = indexes.DateTimeField(model_attr='start_dt')
    end_dt = indexes.DateTimeField(model_attr='end_dt')
    never_expires = indexes.BooleanField(model_attr='never_expires', null=True)
    value = indexes.DecimalField(model_attr='value')
    cap = indexes.IntegerField(model_attr='cap')

    num_of_uses = indexes.IntegerField()

    @classmethod
    def get_model(self):
        return Discount

    def prepare_num_of_uses(self, obj):
        return obj.num_of_uses()
