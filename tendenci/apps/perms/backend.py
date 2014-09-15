from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.db.models.base import Model

from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.utils import can_view


class ObjectPermBackend(object):
    """
    Custom backend that supports tendenci's version of group permissions and
    row level permissions, most of the code is copied from django
    with a few modifications
    """
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username=None, password=None, user=None):
        """
            Modified version of django's authenticate.

            Will accept a user object, bypassing the password check.
            Returns the user for auto_login purposes
        """
        if user:
            if hasattr(user, 'auto_login'):
                if not user.is_anonymous() and user.auto_login:
                    return user
        else:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None

        return None

    def get_group_permissions(self, user_obj):
        """
        Returns a set of permission strings that this user has through his/her
        groups.
        """
        if not hasattr(user_obj, '_group_perm_cache'):
            # tendenci user_groups
            group_perms = Permission.objects.filter(group_permissions__members=user_obj,
                ).values_list('content_type__app_label', 'codename'
                ).order_by()
            group_perms_1 = ["%s.%s" % (ct, name) for ct, name in group_perms]

            # django auth groups
            group_perms = Permission.objects.filter(group__user=user_obj,
                ).values_list('content_type__app_label', 'codename'
                ).order_by()
            group_perms_2 = ["%s.%s" % (ct, name) for ct, name in group_perms]

            user_obj._group_perm_cache = set(group_perms_1 + group_perms_2)

        return user_obj._group_perm_cache

    def get_all_permissions(self, user_obj):
        if user_obj.is_anonymous():
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = set([u"%s.%s" % (p.content_type.app_label, p.codename) for p in user_obj.user_permissions.select_related()])
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
        return user_obj._perm_cache

    def get_group_object_permissions(self, user_obj, obj):
        app_label = obj._meta.app_label
        user_obj_attr = '_%s_%d_group_object_perm_cache' % (
            app_label,
            obj.pk
        )
        if not hasattr(user_obj, user_obj_attr):
            content_type = ContentType.objects.get_for_model(obj)
            filters = {
               'group__members': user_obj,
               'content_type': content_type,
               'object_id': obj.pk
            }
            group_object_perms = ObjectPermission.objects.filter(**filters)
            user_obj._group_object_perm_cache = set([u"%s.%s.%s" % (p.object_id, p.content_type.app_label, p.codename) for p in group_object_perms])
        return user_obj._group_object_perm_cache

    def get_all_object_permissions(self, user_obj, obj):
        app_label = obj._meta.app_label
        user_obj_attr = '_%s_%d_object_perm_cache' % (
            app_label,
            obj.pk
        )
        if not hasattr(user_obj, user_obj_attr):
            content_type = ContentType.objects.get_for_model(obj)
            filters = {
                'content_type': content_type,
                'object_id': obj.pk,
                'user': user_obj
            }
            perms = ObjectPermission.objects.filter(**filters)
            user_obj._object_perm_cache = set([u"%s.%s.%s" % (p.object_id, p.content_type.app_label, p.codename) for p in perms])
            user_obj._object_perm_cache.update(self.get_group_object_permissions(user_obj, obj))
        return user_obj._object_perm_cache

    def has_perm(self, user, perm, obj=None):
        # check codename, return false if its a malformed codename
        try:
            perm_type = perm.split('.')[-1].split('_')[0]
            codename = perm.split('.')[1]
        except IndexError:
            return False

        # check group and user permissions, it check the regular users permissions and
        # the custom groups user permissions
        if perm in self.get_all_permissions(user):
            return True

        if not obj:
            return False

        # they are non-admin, should not view any content with status=False - GJQ
        if hasattr(obj, "status") and not obj.status:
            return False

        # object anonymous and use bits
        if perm_type == 'view':
            has_attr_aov = hasattr(obj, "allow_anonymous_view")
            has_attr_auv = hasattr(obj, "allow_user_view")
            has_attr_amv = hasattr(obj, "allow_member_view")
            if all([has_attr_aov, has_attr_auv, has_attr_amv]):
                if obj.allow_anonymous_view:
                    return True
                if user.is_authenticated() and obj.allow_user_view:
                    return True
                if user.profile.is_member and obj.allow_member_view:
                    return True

        if perm_type == 'change':
            has_attr_aue = hasattr(obj, "allow_user_edit")
            has_attr_ame = hasattr(obj, "allow_member_edit")
            if all([has_attr_aue, has_attr_ame]):
                if user.is_authenticated() and obj.allow_user_edit:
                    return True
                if user.profile.is_member and obj.allow_member_edit:
                    return True

        # no anonymous user currently
        if not user.is_authenticated():
            return False

        # check creator and owner
        if hasattr(obj, 'creator'):
            if obj.creator_id == user.id:
                return True
        if hasattr(obj, 'owner'):
            if obj.owner_id == user.id:
                return True


        if not isinstance(obj, Model):
            return False

        # lets check the search index for view permissions
        # before we ever hit the database, faster
        if 'view' in perm:
            try:  # test for an index and make the query
                from haystack import connections
                site = connections['default'].unified_index()

                index = site.get_index(obj.__class__)
                if can_view(user, obj):
                    return True
            except:
                pass

        # check the permissions on the object level of groups or user
        perm = '%s.%s' % (obj.pk, perm)
        if perm in self.get_all_object_permissions(user, obj):
            return True

    def has_module_perms(self, user_obj, app_label):
        """
        Returns True if user_obj has any permissions in the given app_label.
        """
        for perm in self.get_all_permissions(user_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
