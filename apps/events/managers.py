from datetime import datetime
import operator

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User

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

        # check to see if there is impersonation
        if hasattr(user,'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user
                
        admin = is_admin(user)
            
        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not admin:
                    if not user.is_anonymous():

                        # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                        anon_query = Q(allow_anonymous_view=True)
                        user_query = Q(allow_user_view=True)
                        sec1_query = Q(status=1, status_detail='active')
                        sec2_query = Q(who_can_view__exact=user.username)

                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])

                        sqs = sqs.filter(query)
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
                        # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                        anon_query = Q(allow_anonymous_view=True)
                        user_query = Q(allow_user_view=True)
                        sec1_query = Q(status=1, status_detail='active')
                        sec2_query = Q(who_can_view__exact=user.username)

                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)
            else:
                sqs = sqs.filter(allow_anonymous_view=True)

            sqs = sqs.filter(start_dt__gt = datetime.now())
            sqs = sqs.order_by('start_dt')

        if event:
            sqs = sqs.filter(event=event)

        return sqs.models(self.model)

    def search_filter(self, filters=None, *args, **kwargs):
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)
        admin = is_admin(user)

        # permission filters
        if user:
            if not admin:
                if not user.is_anonymous():
                    # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                    anon_query = Q(allow_anonymous_view=True)
                    user_query = Q(allow_user_view=True)
                    sec1_query = Q(status=1, status_detail='active')
                    sec2_query = Q(who_can_view__exact=user.username)

                    query = reduce(operator.or_, [anon_query, user_query])
                    query = reduce(operator.and_, [sec1_query, query])
                    query = reduce(operator.or_, [query, sec2_query])
                else:
                    sqs = sqs.filter(allow_anonymous_view=True)               
        else:
            sqs = sqs.filter(allow_anonymous_view=True) 

        # custom filters
        for filter in filters:
            sqs = sqs.filter(content='"%s"' % filter)

        return sqs.models(self.model)

class RegistrantManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query events. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()

        user = kwargs.get('user', None)
        event = kwargs.get('event', None)
            
        is_an_admin = is_admin(user)
        
        if event:
            sqs = sqs.filter(event=event)

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not is_an_admin:
                    if not user.is_anonymous():
                        # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                        anon_query = Q(allow_anonymous_view=True)
                        user_query = Q(allow_user_view=True)
                        sec1_query = Q(status=1, status_detail='active')
                        sec2_query = Q(who_can_view__exact=user.username)

                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])
                        sqs = sqs.filter(query)
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
                        # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                        anon_query = Q(allow_anonymous_view=True)
                        user_query = Q(allow_user_view=True)
                        sec1_query = Q(status=1, status_detail='active')
                        sec2_query = Q(who_can_view__exact=user.username)

                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])
                        sqs = sqs.filter(query)
                    else:
                        sqs = sqs.filter(allow_anonymous_view=True)
            else:
                sqs = sqs.filter(allow_anonymous_view=True)

#            sqs = sqs.order_by('-update_dt')
    
        return sqs.models(self.model)