from django.db.models import Manager

from haystack.query import SearchQuerySet

class NewsManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query news. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        
        return sqs.models(self.model).order_by('-create_dt')