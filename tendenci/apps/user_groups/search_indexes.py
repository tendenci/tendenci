from haystack import indexes
from haystack import site

from tendenci.apps.user_groups.models import Group
from tendenci.core.perms.indexes import TendenciBaseSearchIndex


class GroupIndex(TendenciBaseSearchIndex):
    name = indexes.CharField(model_attr='name')
    label = indexes.CharField(model_attr='label')
    type = indexes.CharField(model_attr='type')
    description = indexes.CharField(model_attr='description')
    show_as_option = indexes.BooleanField(model_attr='show_as_option')

site.register(Group, GroupIndex)
