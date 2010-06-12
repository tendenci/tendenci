from django.db.models import Manager

from haystack.query import SearchQuerySet

class FileManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses Haystack to query. 
            Returns a SearchQuerySet
        """
        from files.models import File
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        
        return sqs.models(File).order_by('-create_dt')