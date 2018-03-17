from haystack import indexes

from tendenci.apps.locations.models import Location
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.base.utils import strip_html


class LocationIndex(TendenciBaseSearchIndex, indexes.Indexable):
    description = indexes.CharField(model_attr='description')
    location_name = indexes.CharField(model_attr='location_name')

    @classmethod
    def get_model(self):
        return Location

    def prepare_description(self, obj):
        return strip_html(obj.description)
