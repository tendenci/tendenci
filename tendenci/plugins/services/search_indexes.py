from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from models import Service
from perms.indexes import TendenciBaseSearchIndex

class ServiceIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    activation_dt = indexes.DateTimeField(model_attr='activation_dt', null=True)
    expiration_dt = indexes.DateTimeField(model_attr='expiration_dt', null=True)
    create_dt = indexes.DateTimeField(model_attr='create_dt')
    syndicate = indexes.BooleanField(model_attr='syndicate')

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description

site.register(Service, ServiceIndex)
