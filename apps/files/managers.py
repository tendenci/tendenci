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
            sqs = sqs.auto_query(sqs.query.clean(query))
        else:
            sqs = sqs.all()

        sqs = sqs.order_by('-update_dt')
        
        return sqs.models(File)