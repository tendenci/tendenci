from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex
from products.models import Product

class ProductIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    slug = indexes.CharField(model_attr='slug')
    brand = indexes.CharField(model_attr='brand')
    #url = indexes.CharField(model_attr='url')
    item_number = indexes.CharField(model_attr='item_number')
    category = indexes.CharField()
    subcategory = indexes.CharField()
    summary = indexes.CharField(model_attr='summary')
    description = indexes.CharField(model_attr='description')

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(Product, ProductIndex)
 