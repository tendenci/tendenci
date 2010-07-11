from django.db.models import Manager
from haystack.query import SearchQuerySet

class GroupManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            group haystack to query groups. 
            Returns a SearchQuerySet
        """
        from user_groups.models import Group
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        
        sqs = sqs.order_by('name')
        
        return sqs.models(Group)