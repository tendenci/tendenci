from perms.managers import TendenciBaseManager
from haystack.query import SearchQuerySet

class BeforeAndAfterManager(TendenciBaseManager):
    """
    Model Manager
    """
    
    def search(self, query=None, *args, **kwargs):
        """
        Search the Django Haystack search index
        Returns a SearchQuerySet object
        """
        
        sqs = kwargs.get('sqs', SearchQuerySet())
        
        # filter out the big parts first
        sqs = sqs.models(self.model)
        
        # user information
        user = kwargs.get('user') or AnonymousUser()
        user = self._impersonation(user)
        self.user = user

        # if the status_detail is something like "published"
        # then you can specify the kwargs to override
        status_detail = kwargs.get('status_detail', 'active')

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))
        
        if self.user:
            sqs = self._permissions_sqs(sqs, user, status_detail)
        
        return sqs
