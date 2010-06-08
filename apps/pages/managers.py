from django.db.models import Manager

from haystack.query import SearchQuerySet

class PageManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query pages. 
            Returns a SearchQuerySet
        """
        from pages.models import Page
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        
        return sqs.models(Page)