from haystack import indexes


from django.utils.html import strip_tags, strip_entities

from tendenci.apps.locations.models import Location
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

class LocationIndex(TendenciBaseSearchIndex, indexes.Indexable):
    description = indexes.CharField(model_attr='description')
    location_name = indexes.CharField(model_attr='location_name')

    @classmethod
    def get_model(self):
        return Location

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description


