from haystack import indexes
from haystack import site

from django.utils.html import strip_tags, strip_entities

from tendenci.addons.locations.models import Location
from tendenci.core.perms.indexes import TendenciBaseSearchIndex

class LocationIndex(TendenciBaseSearchIndex):
    description = indexes.CharField(model_attr='description')
    location_name = indexes.CharField(model_attr='location_name')

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description

site.register(Location, LocationIndex)
