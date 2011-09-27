from haystack import indexes
from haystack import site
from django.utils.html import strip_tags, strip_entities

from perms.indexes import TendenciBaseSearchIndex

from models import Video

class VideoIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    position = indexes.CharField(model_attr='position')
    category = indexes.CharField()

    # RSS fields
    order = indexes.DateTimeField()

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description

    def prepare_order(self, obj):
        return obj.create_dt

site.register(Video, VideoIndex)
