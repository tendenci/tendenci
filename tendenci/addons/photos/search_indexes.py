from haystack import indexes
from haystack import site

from django.utils.html import strip_tags, strip_entities

from tendenci.addons.photos.models import PhotoSet, Image
from tendenci.core.perms.indexes import TendenciBaseSearchIndex


class PhotoSetIndex(TendenciBaseSearchIndex):
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_order(self, obj):
        return obj.update_dt


class PhotoIndex(TendenciBaseSearchIndex):
    photo_pk = indexes.IntegerField(model_attr='pk')
    title = indexes.CharField(model_attr='title')
    caption = indexes.CharField(model_attr='caption')
    photosets = indexes.MultiValueField(null=True)

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def prepare_caption(self, obj):
        caption = obj.caption
        caption = strip_tags(caption)
        caption = strip_entities(caption)
        return caption

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
# site.register(Image, PhotoIndex)
