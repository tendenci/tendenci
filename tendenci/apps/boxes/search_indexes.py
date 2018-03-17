from haystack import indexes

from tendenci.apps.boxes.models import Box
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.base.utils import strip_html


class BoxIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    content = indexes.CharField(model_attr='content')

    # RSS fields
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return Box

    def prepare_content(self, obj):
        return strip_html(obj.content)

    def prepare_order(self, obj):
        return obj.update_dt
