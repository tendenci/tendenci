from django.db.models import Manager

from haystack.query import SearchQuerySet
from perms.utils import is_admin

class EventManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query events. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()

        user = kwargs.get('user', None)
        event = kwargs.get('event', None)

        admin = is_admin(user)
            
        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not admin:
                    if not user.is_anonymous():
                        sqs = sqs.filter(allow_user_view=True)
                        sqs = sqs.filter_or(who_can_view__exact=user.username)
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)               
            else:
                sqs = sqs.filter(allow_anonymous_view=True) 
        else:
            if user:
                if admin:
                    sqs = sqs.all()
                else:
                    if not user.is_anonymous():
                        sqs = sqs.filter(allow_user_view=True)
                        sqs = sqs.filter_or(who_can_view__exact=user.username)
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)
            else:
                sqs = sqs.filter(allow_anonymous_view=True)

            sqs = sqs.order_by('-create_dt')


        if event:
            sqs = sqs.filter(event=event)

        return sqs.models(self.model)

class RegistrantManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query events. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        
        if 'user' in kwargs:
            user = kwargs['user']
        else:
            user = None
            
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
                    print sqs
                else:
                    if not user.is_anonymous():
                        sqs = sqs.filter(allow_user_view=True)
                        sqs = sqs.filter_or(who_can_view__exact=user.username)
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)               
            else:
                sqs = sqs.filter(allow_anonymous_view=True)

            sqs = sqs.order_by('-create_dt')
    
        return sqs.models(self.model)