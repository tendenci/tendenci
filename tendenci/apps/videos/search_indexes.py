from haystack import indexes
from django.utils.html import strip_tags, strip_entities

from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

from tendenci.apps.videos.models import Video

class VideoIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    ordering = indexes.IntegerField(model_attr='ordering')
    category = indexes.CharField()

    # RSS fields
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return Video

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description

    def prepare_order(self, obj):
        return obj.create_dt
