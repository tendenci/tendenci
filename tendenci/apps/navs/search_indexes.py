from haystack import indexes


from django.utils.html import strip_tags, strip_entities

from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.navs.models import Nav


class NavIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    megamenu = indexes.BooleanField(model_attr='megamenu', null=True)

    @classmethod
    def get_model(self):
        return Nav


