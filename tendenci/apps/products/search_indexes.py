from haystack import indexes

from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from .models import Product

class ProductIndex(TendenciBaseSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    slug = indexes.CharField(model_attr='slug')
    brand = indexes.CharField(model_attr='brand')
    #url = indexes.CharField(model_attr='url')
    item_number = indexes.CharField(model_attr='item_number')
    category = indexes.CharField()
    summary = indexes.CharField(model_attr='summary')
    description = indexes.CharField(model_attr='description')

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return Product

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_order(self, obj):
        return obj.update_dt

 
