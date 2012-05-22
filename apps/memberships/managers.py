import operator

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User, AnonymousUser

from haystack.query import SearchQuerySet
from perms.managers import TendenciBaseManager
from perms.utils import is_admin, is_member
from site_settings.utils import get_setting
#from memberships.models import Membership

class MemberAppManager(TendenciBaseManager):
    def search(self, query=None, *args, **kwargs):
        # """
        # Uses haystack to query articles.
        # Returns a SearchQuerySet
        # """
        # # update what the status detail should be instead of active
        # kwargs.update({'status_detail': 'published'})
        # return super(MemberAppManager, self).search(query=query, *args, **kwargs)

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
                sqs = anon2_sqs(sqs)  # anonymous
            else:
                pass
                sqs = user2_sqs(sqs, user=user)  # user

        return sqs.models(self.model)


class MemberAppEntryManager(TendenciBaseManager):
    """
    Model Manager
    """
    # TODO: lots of clean up

    # Public functions
    def search(self, query=None, *args, **kwargs):
        """
        Search the Django Haystack search index
        Returns a SearchQuerySet object
        """
        from perms.utils import is_admin, is_member, is_developer

        sqs = kwargs.get('sqs', SearchQuerySet())
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
        
        if is_admin(user) or is_developer(user):
            sqs = sqs.all()
        else:
            if user.is_anonymous():
                sqs = anon3_sqs(sqs, status_detail=status_detail)

            elif is_member(user):
                sqs = self._member_sqs(sqs, user=user,
                status_detail=status_detail)
            else:
                sqs = user3_sqs(sqs, user=user,
                status_detail=status_detail)
                # pass

        return sqs



def user3_sqs(sqs, **kwargs):
    """
    people between admin and anon permission
    (status+status_detail+(anon OR user)) OR (who_can_view__exact)
    """
    user = kwargs.get('user')
    groups = [g.pk for g in user.group_set.all()]
    status_detail = kwargs.get('status_detail', 'active')

    status_q = Q(status=1, status_detail=status_detail)
    creator_q = Q(creator_username=user.username)
    owner_q = Q(owner_username=user.username)
    user_perm_q = Q(users_can_view__in=[user.pk])

    if groups:
        group_perm_q = Q(groups_can_view__in=groups)
        return sqs.filter((status_q&(creator_q|owner_q))|(user_perm_q|group_perm_q))
    else:
        return sqs.filter((status_q&(creator_q|owner_q))|(user_perm_q))

def anon3_sqs(sqs, **kwargs):
    status_detail = kwargs.get('status_detail', 'active')
    sqs = sqs.filter(status=1).filter(status_detail=status_detail)
    # sqs = sqs.filter(allow_anonymous_view=True)
    return sqs

def anon2_sqs(sqs):
    sqs = sqs.filter(status=1).filter(status_detail='published')
    sqs = sqs.filter(allow_anonymous_view=True)
    return sqs

def user2_sqs(sqs, **kwargs):
    """
    people between admin and anon permission
    (status+status_detail+(anon OR user)) OR (who_can_view__exact)
    """
    user = kwargs.get('user', None)

    anon_q = Q(allow_anonymous_view=True)
    user_q = Q(allow_user_view=True)
    status_q = Q(status=1, status_detail='published')
    perm_q = Q(users_can_view__in=user.username)

    q = reduce(operator.or_, [anon_q, user_q])
    q = reduce(operator.and_, [status_q, q])
    q = reduce(operator.or_, [q, perm_q])

    return sqs.filter(q)

def anon_sqs(sqs):
    sqs = sqs.filter(status=1).filter(status_detail='active')
    sqs = sqs.filter(allow_anonymous_view=True)

    member_perms = get_setting('module', 'memberships', 'memberprotection')
    if member_perms != "public":
        sqs = sqs.none()

    return sqs


def user_sqs(sqs, **kwargs):
    """
    people between admin and anon permission
    (status+status_detail+(anon OR user)) OR (who_can_view__exact)
    """
    user = kwargs.get('user')
    member_perms = get_setting('module', 'memberships', 'memberprotection')

    anon_q = Q(allow_anonymous_view=True)
    user_q = Q(allow_user_view=True)
    status_q = Q(status=1, status_detail='active')
    perm_q = Q(users_can_view__in=user.username)

    q = reduce(operator.or_, [anon_q, user_q])
    q = reduce(operator.and_, [status_q, q])
    q = reduce(operator.or_, [q, perm_q])

    filtered_sqs = sqs.filter(q)
    if not is_member(user):
        # all-members means members can view all other members
        if member_perms == "all-members":
            filtered_sqs = filtered_sqs.none()
        # member type means members can only view members of their same type
        if member_perms == "member-type":
            filtered_sqs = filtered_sqs.none()

    return filtered_sqs


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

    def first(self, **kwargs):
        """
        Returns first instance that matches filters.
        If no instance is found then a none type object is returned.
        """
        try:
            instance = self.get(**kwargs)
        except self.model.MultipleObjectsReturned:
            instance = self.filter(**kwargs)[0]
        except self.model.DoesNotExist:
            instance = None

        return instance

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
        Get newest membership record
        Return membership object
        """
        memberships = self.filter(status=1, status_detail='active').order_by('-pk')
        if memberships:
            return memberships[0]

        return None

    def silence_old_memberships(self, user):
        """
        Silence old memberships within their renewal period
        that belong to this user.  Returns a list of the memberships silenced.
        """
        silenced_memberships = []

        # We are only silencing memerships within
        # their renewal period per user, not globally.
        # If user is missing; then we abort.
        if not user:
            return silenced_memberships

        for membership in user.memberships.all():
            if membership.can_renew():
                membership.send_notice = False
                membership.save()
                silenced_memberships.append(membership)

        return silenced_memberships
