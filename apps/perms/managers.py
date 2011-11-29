import operator

from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, AnonymousUser

from haystack.query import SearchQuerySet
from haystack.backends import SQ


class ObjectPermissionManager(models.Manager):
    def users_with_perms(self, perm, instance):
        """
        Checks a permission against an model instance
        and returns a list of users that have that
        permission
        """
        # check codename, return false if its a malformed codename
        try:
            codename = perm.split('.')[1]
        except IndexError:
            return []

        # TODO: create an interface that will allow users
        # to be added to the object permission table
        # this line should be uncommented after that
        return []

        # check the permissions on the object level
        content_type = ContentType.objects.get_for_model(instance)
        filters = {
            "content_type": content_type,
            "object_id": instance.pk,
            "codename": codename,
        }

        permissions = self.select_related().filter(**filters)
        users = []
        if permissions:
            # setup up list of permissions
            for perm in permissions:
                if perm.user:
                    users.append(perm.user.pk)
            return users
        else:
            return []

    def groups_with_perms(self, perm, instance):
        """
        Checks a permission against an model instance
        and returns a list of groups that have that
        permission
        """
        # check codename, return false if its a malformed codename
        try:
            codename = perm.split('.')[1]
        except IndexError:
            return []

        # check the permissions on the object level
        content_type = ContentType.objects.get_for_model(instance)
        filters = {
            "content_type": content_type,
            "object_id": instance.pk,
            "codename": codename,
        }

        permissions = self.select_related().filter(**filters)
        groups = []
        if permissions:
            # setup up list of permissions
            for perm in permissions:
                if perm.group:
                    groups.append(perm.group.pk)
            return groups
        else:
            return []

    def assign_group(self, group_or_groups, object, perms=None):
        """
        Assigns permissions to group or multiple groups
        assign_group(self, group_or_groups, object, perms=None)

        -- group_or_groups: can be a single group object, list, queryset
        or tuple. Although tuples may work differently:
        You can pass permissions individual permissions along with the tuple
        like so: ((instance,'view',),(instance,'change',))

        -- object: is the instance of a model class

        -- perms: a list of individual permissions to assign to each group
           leave blank for all permissions.
           Note: If you are using the tuple/perm approach this does nothing.
        """
        multi_group = False
        group_with_perms = False

        # nobody to give permissions too
        if not group_or_groups:
            return
        # check perms
        if not isinstance(perms, list):
            perms = None
        # check for multi_groups
        if isinstance(group_or_groups, list):
            multi_group = True
        if isinstance(group_or_groups, QuerySet):
            multi_group = True
        if isinstance(group_or_groups, tuple):
            multi_group = True
            if len(group_or_groups[0]) == 2:
                group_with_perms = True

        # treat the tuples differently. They are passed in as
        # ((group,perm,),(group,perm,) ..... (group,perm.))
        if group_with_perms:
            from user_groups.models import Group
            for group, perm in group_or_groups:
                if isinstance(group, unicode):
                    if group.isdigit():
                        try:
                            group = Group.objects.get(pk=group)
                        except:
                            group = None

                codename = '%s_%s' % (perm, object._meta.object_name.lower())
                content_type = ContentType.objects.get_for_model(object)

                perm = Permission.objects.get(codename=codename,
                                              content_type=content_type)

                defaults = {
                    "codename": codename,
                    "object_id": object.pk,
                    "content_type": perm.content_type,
                    "group": group,
                }
                self.get_or_create(**defaults)
            return  # get out

        if multi_group:
            for group in group_or_groups:
                if perms:
                    for perm in perms:
                        codename = '%s_%s' % (perm, object._meta.object_name.lower())
                        content_type = ContentType.objects.get_for_model(object)

                        perm = Permission.objects.get(codename=codename,
                                                      content_type=content_type)

                        defaults = {
                            "codename": codename,
                            "object_id": object.pk,
                            "content_type": perm.content_type,
                            "group": group,
                        }
                        self.get_or_create(**defaults)
                else:  # all default permissions
                    content_type = ContentType.objects.get_for_model(object)
                    perms = Permission.objects.filter(content_type=content_type)
                    for perm in perms:
                        defaults = {
                            "codename": perm.codename,
                            "object_id": object.pk,
                            "content_type": content_type,
                            "group": group,
                        }
                        self.get_or_create(**defaults)
        else:  # not multi_group
            if perms:
                for perm in perms:
                    codename = '%s_%s' % (perm, object._meta.object_name.lower())
                    content_type = ContentType.objects.get_for_model(object)

                    perm = Permission.objects.get(codename=codename,
                                                  content_type=content_type)
                    defaults = {
                        "codename": codename,
                        "object_id": object.pk,
                        "content_type": perm.content_type,
                        "group": group_or_groups,
                    }
                    self.get_or_create(**defaults)
            else:  # all default permissions
                content_type = ContentType.objects.get_for_model(object)
                perms = Permission.objects.filter(content_type=content_type)
                for perm in perms:
                    defaults = {
                        "codename": perm.codename,
                        "object_id": object.pk,
                        "content_type": content_type,
                        "group": group_or_groups,
                    }
                    self.get_or_create(**defaults)

    def assign(self, user_or_users, object, perms=None):
        """
        Assigns permissions to user or multiple users
        assign_group(self, user_or_users, object, perms=None)

        -- user_or_users: can be a single user object, list, queryset
        or tuple.

        -- object: is the instance of a model class

        -- perms: a list of individual permissions to assign to each user
           leave blank for all permissions.
        """
        multi_user = False

        # nobody to give permissions too
        if not user_or_users:
            return
        # check perms
        if not isinstance(perms, list):
            perms = None
        # check for multi_users
        if isinstance(user_or_users, list):
            multi_user = True
        if isinstance(user_or_users, QuerySet):
            multi_user = True
        if isinstance(user_or_users, tuple):
            multi_user = True

        if multi_user:
            for user in user_or_users:
                if perms:
                    for perm in perms:
                        codename = '%s_%s' % (perm, object._meta.object_name.lower())
                        content_type = ContentType.objects.get_for_model(object)

                        perm = Permission.objects.get(codename=codename,
                                                      content_type=content_type)

                        defaults = {
                            "codename": codename,
                            "object_id": object.pk,
                            "content_type": perm.content_type,
                            "user": user,
                        }
                        try:
                            self.get_or_create(**defaults)
                        except self.model.MultipleObjectsReturned as e:
                            pass

                else:  # all default permissions
                    content_type = ContentType.objects.get_for_model(object)
                    perms = Permission.objects.filter(content_type=content_type)
                    for perm in perms:
                        defaults = {
                            "codename": perm.codename,
                            "object_id": object.pk,
                            "content_type": content_type,
                            "user": user,
                        }
                        try:
                            self.get_or_create(**defaults)
                        except self.model.MultipleObjectsReturned as e:
                            pass

        else:  # not muli_user
            if perms:
                for perm in perms:
                    codename = '%s_%s' % (perm, object._meta.object_name.lower())
                    content_type = ContentType.objects.get_for_model(object)

                    perm = Permission.objects.get(codename=codename,
                                                  content_type=content_type)
                    defaults = {
                        "codename": codename,
                        "object_id": object.pk,
                        "content_type": perm.content_type,
                        "user": user_or_users,
                    }
                    try:
                        self.get_or_create(**defaults)
                    except self.model.MultipleObjectsReturned as e:
                        pass

            else:  # all default permissions
                content_type = ContentType.objects.get_for_model(object)
                perms = Permission.objects.filter(content_type=content_type)
                for perm in perms:
                    defaults = {
                        "codename": perm.codename,
                        "object_id": object.pk,
                        "content_type": content_type,
                        "user": user_or_users,
                    }
                    try:
                        self.get_or_create(**defaults)
                    except self.model.MultipleObjectsReturned as e:
                        pass

    def remove_all(self, object):
        """
            Remove all permissions on object (instance)
        """
        content_type = ContentType.objects.get_for_model(object)
        perms = self.filter(content_type=content_type,
                            object_id=object.pk)
        for perm in perms:
            perm.delete()


class TendenciBaseManager(models.Manager):
    """
    Base manager for all TendenciBase models
    """
    user = None

    # Private functions
    def _anon_sqs(self, sqs, **kwargs):
        """
        Filter the query set for anonymous users
        """
        status_detail = kwargs.get('status_detail', 'active')
        status = kwargs.get('status', True)

        sqs = sqs.filter(
            allow_anonymous_view=True,
            status=status,
            status_detail=status_detail)
        return sqs

    def _member_sqs(self, sqs, user, **kwargs):
        """
        Filter the query set for members.

        (status AND status_detail AND
        (anon_view OR user_view OR member_view))
        OR
        (users_can_view__in user.pk)
        OR
        (groups_can_view__in user's groups)

        user is a required argument since we'll be filtering by user.pk.
        """
        groups = [g.pk for g in user.group_set.all()]
        status_detail = kwargs.get('status_detail', 'active')
        status = kwargs.get('status', True)

        anon_q = SQ(allow_anonymous_view=True)
        user_q = SQ(allow_user_view=True)
        member_q = SQ(allow_member_view=True)
        status_q = SQ(status=status, status_detail=status_detail)
        user_perm_q = SQ(users_can_view__in=[user.pk])
        group_perm_q = SQ(groups_can_view__in=groups)

        if groups:
            sqs = sqs.filter(
                (status_q & (anon_q | user_q)) |
                (user_perm_q | group_perm_q))
        else:
            pass
            sqs = sqs.filter(
                (status_q & (anon_q | user_q)) |
                (user_perm_q))

        return sqs

    def _user_sqs(self, sqs, user, **kwargs):
        """
        Filter the query set for people between admin and anon permission

        (status AND status_detail AND ((anon_view OR user_view)
        OR
        (users_can_view__in user.pk)
        OR
        (groups_can_view__in user's groups)

        user required since we'll filter by user.pk.
        """
        groups = [g.pk for g in user.group_set.all()]
        status_detail = kwargs.get('status_detail', 'active')
        status = kwargs.get('status', True)

        anon_q = SQ(allow_anonymous_view=True)
        user_q = SQ(allow_user_view=True)
        status_q = SQ(status=status, status_detail=status_detail)
        user_perm_q = SQ(users_can_view__in=[user.pk])
        group_perm_q = SQ(groups_can_view__in=groups)

        if groups:
            sqs = sqs.filter(
                (status_q & (anon_q | user_q)) |
                (user_perm_q | group_perm_q))
        else:
            sqs = sqs.filter(
                (status_q & (anon_q | user_q)) |
                (user_perm_q)
            )

        return sqs

    def _impersonation(self, user):
        """
        Test for impersonation and return the impersonee
        """
        if hasattr(user, 'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user
        return user

    def _permissions_sqs(self, sqs, user, status, status_detail):
        from perms.utils import is_admin, is_member, is_developer
        if is_admin(user) or is_developer(user):
            sqs = sqs.all()
        else:
            if user.is_anonymous():
                sqs = self._anon_sqs(sqs, status=status, status_detail=status_detail)
            elif is_member(user):
                sqs = self._member_sqs(sqs, user, status=status,
                    status_detail=status_detail)
            else:
                sqs = self._user_sqs(sqs, user, status=status,
                    status_detail=status_detail)
        return sqs

    # Public functions
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
        status = kwargs.get('status', True)

        if query:
            sqs = sqs.auto_query(sqs.query.clean(query))

        sqs = self._permissions_sqs(sqs, user, status, status_detail)

        return sqs
