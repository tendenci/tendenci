from django.db.models import Manager

from haystack.query import SearchQuerySet

class StoryManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query stories. 
            Returns a SearchQuerySet
        """
        from stories.models import Story
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        
        return sqs.models(Story)