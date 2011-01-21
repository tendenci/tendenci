from django.db.models import Manager
from haystack.query import SearchQuerySet

class CorporateMembershipManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            haystack to query corporate memberships. 
            Returns a SearchQuerySet
        """
        from corporate_memberships.models import CorporateMembership
        sqs = SearchQuerySet()
       
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        #sqs = sqs.order_by('user')
        
        return sqs.models(CorporateMembership)