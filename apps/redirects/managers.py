from django.db.models import Manager

from haystack.query import SearchQuerySet
from perms.utils import is_admin

class RedirectManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query news. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)
        is_an_admin = is_admin(user)
            
        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not is_an_admin:
                    return []
        else:
            sqs = sqs.all()
            if user:
                if not is_an_admin:
                    return []
    
        return sqs.models(self.model).order_by('-update_dt')