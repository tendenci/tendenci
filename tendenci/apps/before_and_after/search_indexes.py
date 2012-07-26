from haystack import indexes
from haystack import site

from tendenci.apps.before_and_after.models import BeforeAndAfter

from tendenci.core.perms.indexes import TendenciBaseSearchIndex

class BeforeAndAfterIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    category = indexes.CharField()
    subcategory = indexes.CharField(null=True)
    ordering = indexes.IntegerField(model_attr='ordering')

    def prepare_category(self, obj):
        return obj.category.pk
        
    def prepare_subcategory(self, obj):
        if obj.subcategory:
            return obj.subcategory.pk
        return None

site.register(BeforeAndAfter, BeforeAndAfterIndex)
