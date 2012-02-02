from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from files.models import File
from perms.indexes import TendenciBaseSearchIndex

class FileIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    file = indexes.CharField(model_attr='file')
    description = indexes.CharField(model_attr='description')

    type = indexes.CharField()
    clicks = indexes.IntegerField()

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description
        
    def prepare_type(self, obj):
        return obj.type()
    
    def prepare_clicks(self, obj):
        """
        Return integer of views/downloads per file
        We do a calculation for all files except images.
        """
        from django.contrib.contenttypes.models import ContentType
        from event_logs.models import EventLog

        # calculate click if not image
        if obj.type() != 'image':
            content_type = ContentType.objects.get_for_model(File)
            return EventLog.objects.filter(content_type=content_type, object_id=obj.pk).count()

        return int()  # return 0; data type integer

site.register(File, FileIndex)
