from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from pages.models import Page

class PageIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    content = indexes.CharField(model_attr='content')
    status = indexes.IntegerField(model_attr='status')
    create_dt = indexes.DateTimeField(model_attr='create_dt', null=True)
    
    def prepare_content(self, obj):
        content = obj.content
        content = strip_tags(content)
        content = strip_entities(content)
        return content
    
site.register(Page, PageIndex)