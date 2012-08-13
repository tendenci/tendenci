from haystack.query import SearchQuerySet

from django.db.models import Manager
from django.db.models import Q


class CorporateMembershipManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        haystack to query corporate memberships.
        Returns a SearchQuerySet
        """
        from tendenci.addons.corporate_memberships.models import CorporateMembership

        sqs = SearchQuerySet().models(CorporateMembership)

        if query:
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
            
        # the filter logic for the permission is handled in the search view
        
        return sqs
