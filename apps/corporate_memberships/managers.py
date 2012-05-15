from django.db.models import Manager
from django.db.models import Q
from haystack.query import SearchQuerySet


class CorporateMembershipManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        haystack to query corporate memberships.
        Returns a SearchQuerySet
        """
        from corporate_memberships.models import CorporateMembership
        from perms.utils import is_admin

        sqs = SearchQuerySet().models(CorporateMembership)

        if query:
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
            
        # the filter logic for the permission is handled in the search view
        
        return sqs
