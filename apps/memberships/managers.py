import operator

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User, AnonymousUser

from haystack.query import SearchQuerySet
from perms.managers import TendenciBaseManager
from perms.utils import is_admin


class MemberAppManager(TendenciBaseManager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query articles.
        Returns a SearchQuerySet
        """
        # update what the status detail should be instead of active
        kwargs.update({'status_detail': 'published'})
        return super(MemberAppManager, self).search(query=query, *args, **kwargs)


class MemberAppEntryManager(TendenciBaseManager):
    """
    Model Manager
    """
    pass


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
    if hasattr(user, 'impersonated_user'):
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
            sqs = sqs.all()  # admin
        else:
            if user.is_anonymous():
                sqs = anon_sqs(sqs)  # anonymous
            else:
                sqs = user_sqs(sqs, user=user)  # user

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
