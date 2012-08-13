from haystack import indexes
from haystack import site

from django.utils.html import strip_tags, strip_entities

from tendenci.core.perms.indexes import TendenciBaseSearchIndex
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.apps.navs.models import Nav


class NavIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    megamenu = indexes.BooleanField(model_attr='megamenu')

site.register(Nav, NavIndex)
