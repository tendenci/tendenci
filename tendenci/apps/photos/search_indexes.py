from haystack import indexes

from tendenci.apps.photos.models import PhotoSet, Image
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.base.utils import strip_html


class PhotoSetIndex(TendenciBaseSearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')

    # RSS fields
    can_syndicate = indexes.BooleanField(null=True)
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return PhotoSet

    def prepare_description(self, obj):
        return strip_html(obj.description)

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_order(self, obj):
        return obj.update_dt
