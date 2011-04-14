import operator

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User, AnonymousUser

from haystack.query import SearchQuerySet
from perms.utils import is_admin


class MemberAppManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query articles. 
        Returns a SearchQuerySet
        """
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
                    # if b/w admin and anon

                        # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                        anon_query = Q(**{'allow_anonymous_view':True,})
                        user_query = Q(**{'allow_user_view':True,})
                        sec1_query = Q(**{
                            'status':1,
                            'status_detail':'published',
                        })
                        sec2_query = Q(**{
                            'who_can_view__exact':user.username
                        })
                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])

                        sqs = sqs.filter(query)
                    else:
                    # if anonymous
                        sqs = sqs.filter(status=1).filter(status_detail='published')
                        sqs = sqs.filter(allow_anonymous_view=True)
            else:
                # if anonymous
                sqs = sqs.filter(status=1).filter(status_detail='published')
                sqs = sqs.filter(allow_anonymous_view=True)
        else:
            if user:
                if is_an_admin:
                    sqs = sqs.all()
                else:
                    if not user.is_anonymous():
                        # (status+status_detail+anon OR who_can_view__exact)
                        sec1_query = Q(**{
                            'status':1,
                            'status_detail':'published',
                            'allow_anonymous_view':True,
                        })
                        sec2_query = Q(**{
                            'who_can_view__exact':user.username
                        })
                        query = reduce(operator.or_, [sec1_query, sec2_query])
                        sqs = sqs.filter(query)
                    else:
                        # if anonymous
                        sqs = sqs.filter(status=1).filter(status_detail='published')
                        sqs = sqs.filter(allow_anonymous_view=True)               
            else:
                # if anonymous
                sqs = sqs.filter(status=1).filter(status_detail='published')
                sqs = sqs.filter(allow_anonymous_view=True)
    
        return sqs.models(self.model)

class MemberAppEntryManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query articles. 
        Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)

        # check to see if there is impersonation
        if hasattr(user,'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))

        return sqs.models(self.model)

def anon_sqs(sqs):
    sqs = sqs.filter(status=1).filter(status_detail='active')
    sqs = sqs.filter(allow_anonymous_view=True)
    return sqs

def user_sqs(sqs, **kwargs):
    """
    people between admin and anon permission
    (status+status_detail+(anon OR user)) OR (who_can_view__exact)
    """
    user = kwargs.get('user', None)

    anon_q = Q(allow_anonymous_view=True)
    user_q = Q(allow_user_view=True)
    status_q = Q(status=1, status_detail='active')
    perm_q = Q(who_can_view__exact=user.username)

    q = reduce(operator.or_, [anon_q, user_q])
    q = reduce(operator.and_, [status_q, q])
    q = reduce(operator.or_, [q, perm_q])

    return sqs.filter(q)

def impersonation(user):
    # check to see if there is impersonation
    if hasattr(user,'impersonated_user'):
        if isinstance(user.impersonated_user, User):
            user = user.impersonated_user

    return user

class MembershipManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        Use Django Haystack search index
        Returns a SearchQuerySet object
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', AnonymousUser())
        user = impersonation(user)

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))

        if is_admin(user):
            sqs = sqs.all() # admin
        else:
            if user.is_anonymous():
                sqs = anon_sqs(sqs) # anonymous
            else:
                sqs = user_sqs(sqs, user=user) # user

        return sqs.models(self.model)

    def corp_roster_search(self, query=None, *args, **kwargs):
        """
        Use Django Haystack search index
        Used by the corporate membership roster search 
        which requires different security check
        """
        sqs = SearchQuerySet()
        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))

        return sqs.models(self.model)

    def get_membership(self):
        """
            Get membership object
        """
        try:
            return self.order_by('-pk')[0]
        except:
            return None