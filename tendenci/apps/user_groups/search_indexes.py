from haystack import indexes


from tendenci.apps.user_groups.models import Group
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class GroupIndex(TendenciBaseSearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    label = indexes.CharField(model_attr='label')
    type = indexes.CharField(model_attr='type')
    description = indexes.CharField(model_attr='description')
    show_as_option = indexes.BooleanField(model_attr='show_as_option', null=True)

    @classmethod
    def get_model(self):
        return Group
