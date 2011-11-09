from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex

from attorneys.models import Attorney

class AttorneyIndex(TendenciBaseSearchIndex):
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')
    category = indexes.CharField(model_attr='category')
    position = indexes.CharField(model_attr='position')
    address = indexes.CharField(model_attr='address')
    address2 = indexes.CharField(model_attr='address2')
    city = indexes.CharField(model_attr='city')
    state = indexes.CharField(model_attr='state')
    zip = indexes.CharField(model_attr='zip')
    ordering = indexes.IntegerField(model_attr='ordering')

site.register(Attorney, AttorneyIndex)
