from haystack import indexes
from haystack import site

from django.utils.html import strip_tags, strip_entities

from tendenci.core.files.models import File
from tendenci.core.perms.indexes import TendenciBaseSearchIndex
from tendenci.core.categories.models import Category


class FileIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    file = indexes.CharField(model_attr='file')
    description = indexes.CharField(model_attr='description')

    type = indexes.CharField()
    clicks = indexes.IntegerField()
    group_id = indexes.IntegerField()

    # categories
    category = indexes.CharField()
    sub_category = indexes.CharField()

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description
        
    def prepare_type(self, obj):
        return obj.type()
    
    def prepare_group_id(self, obj):
        if obj.group_id:
            return int(obj.group_id)
        return int()

    def prepare_clicks(self, obj):
        """
        Return integer of views/downloads per file
        We do a calculation for all files except images.
        """
        from django.contrib.contenttypes.models import ContentType
        from tendenci.core.event_logs.models import EventLog

        # calculate click if not image
        if obj.type() != 'image':
            content_type = ContentType.objects.get_for_model(File)
            return EventLog.objects.filter(content_type=content_type, object_id=obj.pk).count()

        return int()  # return 0; data type integer

    def prepare_category(self, obj):
        category = Category.objects.get_for_object(obj, 'category')
        if category:
            return category.name
        return ''

    def prepare_sub_category(self, obj):
        category = Category.objects.get_for_object(obj, 'sub_category')
        if category:
            return category.name
        return ''

# Removed from index after search view was updated to perform
# all searches on the database.
# site.register(File, FileIndex)
