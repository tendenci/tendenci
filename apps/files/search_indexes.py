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
    
    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description
        
    def prepare_type(self, obj):
        return obj.type()

site.register(File, FileIndex)
