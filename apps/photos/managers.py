from django.db.models import Manager

from haystack.query import SearchQuerySet

class PhotoSetManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses Haystack to query. 
            Returns a SearchQuerySet
        """
        from photos.models import PhotoSet
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        
        return sqs.models(PhotoSet).order_by('-create_dt')