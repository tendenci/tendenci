from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex

from models import Staff

class StaffIndex(TendenciBaseSearchIndex):
    name = indexes.CharField(model_attr='name')
    department = indexes.CharField(model_attr='department', null=True)
    position = indexes.CharField(model_attr='position', null=True)
    start_date = indexes.DateField(model_attr='start_date')

site.register(Staff, StaffIndex)
