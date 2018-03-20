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


class PhotoIndex(TendenciBaseSearchIndex, indexes.Indexable):
    photo_pk = indexes.IntegerField(model_attr='pk')
    title = indexes.CharField(model_attr='title')
    caption = indexes.CharField(model_attr='caption')
    photosets = indexes.MultiValueField(null=True)

    # RSS fields
    can_syndicate = indexes.BooleanField(null=True)
    order = indexes.DateTimeField()

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    @classmethod
    def get_model(self):
        return Image

    def prepare_caption(self, obj):
        return strip_html(obj.caption)

    def prepare_photosets(self, obj):
        if obj.photoset.all():
            return [photoset.pk for photoset in obj.photoset.all()]
        return None

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
         and obj.status_detail == 'active'

    def prepare_order(self, obj):
        return obj.update_dt


# Removed from index after search view was updated to perform
# all searches on the database.
# site.register(PhotoSet, PhotoSetIndex)
#
