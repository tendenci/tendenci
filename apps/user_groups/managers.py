from django.db.models import Manager
from haystack.query import SearchQuerySet

class GroupManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            invoice haystack to query invoices. 
            Returns a SearchQuerySet
        """
        from user_groups.models import Group
        sqs = SearchQuerySet()
       
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        #sqs = sqs.order_by('user')
        
        return sqs.models(Group)