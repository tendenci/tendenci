from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from perms.indexes import TendenciBaseSearchIndex
from perms.object_perms import ObjectPermission
from navs.models import Nav

class NavIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    megamenu = indexes.BooleanField(model_attr='megamenu')

site.register(Nav, NavIndex)
