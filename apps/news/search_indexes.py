from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from news.models import News

class NewsIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    headline = indexes.CharField(model_attr='headline')
    body = indexes.CharField(model_attr='body')
    status = indexes.IntegerField(model_attr='status')
    release_dt = indexes.DateTimeField(model_attr='release_dt', null=True)
    
    def prepare_body(self, obj):
        body = obj.body
        body = strip_tags(body)
        body = strip_entities(body)
        return body
    
site.register(News, NewsIndex)