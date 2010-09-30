from django.db.models import Manager
from django.contrib.auth.models import User

from haystack.query import SearchQuerySet

class EntityManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query articles. 
            Returns a SearchQuerySet
        """
        from perms.utils import is_admin
        sqs = SearchQuerySet()
        
        user = kwargs.get('user', None)
            
        # check to see if there is impersonation
        if hasattr(user,'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user
                
        is_an_admin = is_admin(user)
            
        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not is_an_admin:
                    if not user.is_anonymous():
                        sqs = sqs.filter(allow_user_view=True)
                        sqs = sqs.filter_or(who_can_view__exact=user.username)
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)               
            else:
                sqs = sqs.filter(allow_anonymous_view=True) 
        else:
            if user:
                if is_an_admin:
                    sqs = sqs.all()
                else:
                    if not user.is_anonymous():
                        sqs = sqs.filter(allow_user_view=True)
                        sqs = sqs.filter_or(who_can_view__exact=user.username)
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)               
            else:
                sqs = sqs.filter(allow_anonymous_view=True)

            sqs = sqs.order_by('entity_name')
    
        return sqs.models(self.model)