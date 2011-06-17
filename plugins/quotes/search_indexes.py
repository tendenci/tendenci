from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex

from quotes.models import Quote

class QuoteIndex(TendenciBaseSearchIndex):
    quote = indexes.CharField(model_attr='quote')
    author = indexes.CharField(model_attr='author')
    source = indexes.CharField(model_attr='source')
    
    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()
    
    def prepare_quote(self, obj):
        quote = obj.quote
        quote = strip_tags(quote)
        quote = strip_entities(quote)
        return quote
    
    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view \
                and obj.status == 1  and obj.status_detail == 'active'
    
    def prepare_order(self, obj):
        return obj.create_dt

site.register(Quote, QuoteIndex)
