import operator
from dateutil.relativedelta import relativedelta
from datetime import datetime
from functools import reduce

from django.db.models import Q
from django.contrib.auth.models import User

from tendenci.apps.perms.managers import TendenciBaseManager
from tendenci.apps.site_settings.utils import get_setting


def user3_sqs(sqs, **kwargs):
    """
    people between admin and anon permission
    (status+status_detail+(anon OR user)) OR (who_can_view__exact)
    """
    user = kwargs.get('user')
    groups = [g.pk for g in user.group_set.all()]
    status_detail = kwargs.get('status_detail', 'active')

    status_q = Q(status=True, status_detail=status_detail)
    creator_q = Q(creator_username=user.username)
    owner_q = Q(owner_username=user.username)
    user_perm_q = Q(users_can_view__in=[user.pk])

    if groups:
        group_perm_q = Q(groups_can_view__in=groups)
        return sqs.filter((status_q & (creator_q | owner_q)) | (user_perm_q | group_perm_q))
    else:
        return sqs.filter((status_q & (creator_q | owner_q)) | (user_perm_q))


def anon3_sqs(sqs, **kwargs):
    status_detail = kwargs.get('status_detail', 'active')
    sqs = sqs.filter(status=True).filter(status_detail=status_detail)
    # sqs = sqs.filter(allow_anonymous_view=True)
    return sqs


def anon2_sqs(sqs):
    sqs = sqs.filter(status=True).filter(status_detail='published')
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
    status_q = Q(status=True, status_detail='published')
    perm_q = Q(users_can_view__in=user.username)

    q = reduce(operator.or_, [anon_q, user_q])
    q = reduce(operator.and_, [status_q, q])
    q = reduce(operator.or_, [q, perm_q])

    return sqs.filter(q)


def anon_sqs(sqs):
    sqs = sqs.filter(status=True).filter(status_detail='active')
    sqs = sqs.filter(allow_anonymous_view=True)

    member_perms = get_setting('module', 'memberships', 'memberprotection')
    if member_perms != "public":
        sqs = sqs.none()

    return sqs


def member_sqs(sqs, **kwargs):
    """
    users who are members
    (status+status_detail+(anon OR user OR member)) OR (who_can_view__exact)
    """
    user = kwargs.get('user')

    anon_q = Q(allow_anonymous_view=True)
    user_q = Q(allow_user_view=True)
    member_q = Q(allow_member_view=True)
    status_q = Q(status=True, status_detail='active')
    perm_q = Q(users_can_view__in=user.username)

    q = reduce(operator.or_, [anon_q, user_q, member_q])
    q = reduce(operator.and_, [status_q, q])
    q = reduce(operator.or_, [q, perm_q])

    filtered_sqs = sqs.filter(q)

    return filtered_sqs


def user_sqs(sqs, **kwargs):
    """
    people between admin and anon permission
    (status+status_detail+(anon OR user)) OR (who_can_view__exact)
    """
    user = kwargs.get('user')
    member_perms = get_setting('module', 'memberships', 'memberprotection')

    anon_q = Q(allow_anonymous_view=True)
    user_q = Q(allow_user_view=True)
    status_q = Q(status=True, status_detail='active')
    perm_q = Q(users_can_view__in=user.username)

    q = reduce(operator.or_, [anon_q, user_q])
    q = reduce(operator.and_, [status_q, q])
    q = reduce(operator.or_, [q, perm_q])

    filtered_sqs = sqs.filter(q)
    if not user.profile.is_member:
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


class MembershipDefaultManager(TendenciBaseManager):
    def first(self, **kwargs):
        """
        Returns first instance that matches filters.
        If no instance is found then a none type object is returned.
        """
        [instance] = self.filter(**kwargs).order_by('pk')[:1] or [None]
        return instance

    def active(self, **kwargs):
        """
        Returns active memberships
        """
        kwargs['status'] = kwargs.get('status', True)
        kwargs['status_detail'] = kwargs.get('status_detail', 'active')
        return self.filter(
            Q(expire_dt__gt=datetime.now()) | Q(expire_dt__isnull=True), **kwargs)

    def expired(self, **kwargs):
        """
        Returns memberships records that are expired. Considers records
        that are expired, include records that have a status detail of 'expired'.
        """
        from tendenci.apps.memberships.models import MembershipType

        qs = self.none()

        m_types = MembershipType.objects.filter(status=True, status_detail='active')
        for m_type in m_types:

            grace_period = m_type.expiration_grace_period
            expire_dt = datetime.now() + relativedelta(days=grace_period)

            qs = qs | self.filter(
                status=True,
                membership_type=m_type,
                expire_dt__lte=expire_dt,
            )

        qs = qs | self.filter(
            status=True,
            status_detail='expired',
        )

        return qs


class MembershipAppManager(TendenciBaseManager):
    def current_app(self, **kwargs):
        """
        Returns the app being used currently.
        """
        [current_app] = self.filter(
                           status=True,
                           status_detail__in=['active', 'published']
                           ).order_by('id')[:1] or [None]

        return current_app

class MembershipTypeManager(TendenciBaseManager):
    pass
