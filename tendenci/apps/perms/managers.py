from haystack.query import SearchQuerySet
from haystack.backends import SQ

from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, AnonymousUser


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
            from tendenci.apps.user_groups.models import Group
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

    def list_all(self, object):
        """
        Return a list of all permissions
        """
        content_type = ContentType.objects.get_for_model(object)
        perms = self.filter(
            content_type=content_type,
            object_id=object.pk)

        return perms

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

        creator_q = SQ(creator_id=user.id)
        owner_q = SQ(owner_id=user.id)

        if groups:
            sqs = sqs.filter(
                (status_q & (anon_q | user_q | creator_q | owner_q)) |
                (user_perm_q | group_perm_q))
        else:
            sqs = sqs.filter(
                (status_q & (anon_q | user_q | creator_q | owner_q)) |
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

        creator_q = SQ(creator_id=user.id)
        owner_q = SQ(owner_id=user.id)

        if groups:
            sqs = sqs.filter(
                (status_q & (anon_q | user_q | creator_q | owner_q)) |
                (user_perm_q | group_perm_q))
        else:
            sqs = sqs.filter(
                (status_q & (anon_q | user_q | creator_q | owner_q)) |
                (user_perm_q)
            )

        return sqs

    def _user_or_member_sqs(self, sqs, user, **kwargs):
        """
        Filter the query set for user or members.

        Here we check the existence of the fields to be tested,
        and handle the queries that need to be directly pulled from db.

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
        is_member = kwargs.get('is_member', True)

        # allow_xxx and creator and owner fields to be checked
        fields_ors_sq = None
        fields_ors_sq_list = []
        model_fiels =[field.name for field in self.model._meta.fields]

        if 'allow_anonymous_view' in model_fiels:
            fields_ors_sq_list.append(SQ(allow_anonymous_view=True))
        if 'allow_user_view' in model_fiels:
            fields_ors_sq_list.append(SQ(allow_user_view=True))
        if is_member:
            if 'allow_member_view' in model_fiels:
                fields_ors_sq_list.append(SQ(allow_member_view=True))
        if 'creator_username' in model_fiels:
            fields_ors_sq_list.append(SQ(creator_username=user.username))
        if 'owner_username' in model_fiels:
            fields_ors_sq_list.append(SQ(owner_username=user.username))

        for field_sq in fields_ors_sq_list:
            if fields_ors_sq:
                fields_ors_sq = fields_ors_sq | field_sq
            else:
                fields_ors_sq = field_sq

        # status and status_detail if exist
        status_d = {}
        if 'status' in model_fiels:
            status_d.update({'status': status})
        if 'status_detail' in model_fiels:
            status_d.update({'status_detail': status_detail})

        if status_d:
            status_q = SQ(**status_d)
        else:
            status_q = None

        direct_db = kwargs.get('direct_db', 0)

        # object permissions

        if not direct_db:
            group_perm_q = SQ(groups_can_view__in=groups)
            # user is not being recorded in the ObjectPermission
            #user_perm_q = SQ(users_can_view__in=[user.pk])
        else:
            # to pull directly from db, get a list of object_ids instead of groups
            from tendenci.apps.perms.object_perms import ObjectPermission

            app_label = self.model._meta.app_label
            model_name = self.model.__name__
            content_type = ContentType.objects.filter(
                                        app_label=app_label,
                                        model=model_name)[:1]
            codename = 'view_%s' % model_name
            group_allowed_object_ids = ObjectPermission.objects.filter(
                                            content_type=content_type[0],
                                            codename=codename,
                                            group__in=groups).values_list('id', flat=True)
            group_perm_q = SQ(id__in=group_allowed_object_ids)

            # user is not being recorded in the ObjectPermission
            # so, commenting it out for now
#            user_allowed_object_ids = ObjectPermission.objects.filter(
#                                            content_type=content_type[0],
#                                            codename=codename,
#                                            user__in=[user]).values_list('id', flat=True)
            group_perm_q = SQ(id__in=group_allowed_object_ids)


        filters = None
        if status_q or fields_ors_sq:
            if status_q and fields_ors_sq:
                filters = status_q & fields_ors_sq
            elif status_q:
                filters = status_q
            else:
                filters = fields_ors_sq

        if groups:
            if not filters:
                filters = group_perm_q
            else:
                filters = filters | group_perm_q

        if filters:
            sqs = sqs.filter(filters)

        return sqs

    def _impersonation(self, user):
        """
        Test for impersonation and return the impersonee
        """
        if hasattr(user, 'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user
        return user

    def _permissions_sqs(self, sqs, user, status_detail, **kwargs):
        if user.is_authenticated() and user.profile.is_superuser:
            return sqs

        if user.is_anonymous():
            sqs = self._anon_sqs(sqs, status_detail=status_detail)
        elif user.profile.is_member:
            sqs = self._member_sqs(sqs, user,
                status_detail=status_detail)
        else:
            sqs = self._user_sqs(sqs, user,
                status_detail=status_detail)

        return sqs

    # Public functions
    def search(self, query=None, *args, **kwargs):
        """
        Search the Django Haystack search index
        Returns a SearchQuerySet object
        """
        sqs = kwargs.get('sqs', SearchQuerySet())
        direct_db = kwargs.get('direct_db', 0)

        # filter out the big parts first
        if not direct_db:
            sqs = sqs.models(self.model)

        # user information
        user = kwargs.get('user') or AnonymousUser()
        user = self._impersonation(user)
        self.user = user

        # if the status_detail is something like "published"
        # then you can specify the kwargs to override
        status_detail = kwargs.get('status_detail', 'active')

        if query:
            tags_query = kwargs.get('tags-query', False)
            if tags_query:
                query = query.split(':')[1]
                sqs = sqs.filter(tags=sqs.query.clean(query))
            else:
                sqs = sqs.auto_query(sqs.query.clean(query))

        sqs = self._permissions_sqs(sqs, user, status_detail, direct_db=direct_db)

        return sqs

    def first(self, **kwargs):
        """
        Returns first instance that matches filters.
        If no instance is found then a none type object is returned.
        """

        [instance] = self.filter(**kwargs).order_by('pk')[:1] or [None]
        return instance

    def get_queryset(self):
        """
        Returns the queryset only with active objects that have
        a status=True. Objects with status=False are considered
        deleted and should not appear in querysets.
        """
        return super(TendenciBaseManager, self).get_queryset().filter(status=True)

    def all_inactive(self):
        """
        Returns the queryset only with inactive objects that have
        a status=False. It can be chained with filter and other functions,
        but be sure to call this function first.
        """
        return super(TendenciBaseManager, self).get_queryset().filter(status=False)

