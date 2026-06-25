from haystack import indexes

from tendenci.apps.videos.models import Video
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.base.utils import strip_html


class VideoIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    category = indexes.CharField()

    # RSS fields
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return Video

    def prepare_description(self, obj):
        return strip_html(obj.description)

    def prepare_order(self, obj):
        return obj.create_dt
