from django.db.models import Manager

from haystack.query import SearchQuerySet

class ArticleManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query articles. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        
        if 'user' in kwargs:
            user = kwargs['user']
        else:
            user = None
            
        is_admin = user.is_superuser and user.is_active
            
        if query:
            sqs = sqs.filter(content=sqs.query.clean(query)) 
            if user:
                if not is_admin:
                    if not user.is_anonymous():
                        sqs = sqs.filter(allow_user_view=True)
                        sqs = sqs.filter_or(who_can_view__exact=user.username)
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)               
            else:
                sqs = sqs.filter(allow_anonymous_view=True) 
        else:
            if user:
                if not is_admin:
                    if not user.is_anonymous():
                        sqs = sqs.filter(allow_user_view=True)
                        sqs = sqs.filter_or(who_can_view__exact=user.username)
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)                
            else:
                sqs = sqs.filter(allow_anonymous_view=True) 
    
        return sqs.models(self.model)