from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from perms.models import ObjectPermission

class ObjectPermBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True

    # TODO: Model, login attribute name and password attribute name should be
    # configurable.
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_group_permissions(self, user_obj):
        """
        Returns a set of permission strings that this user has through his/her
        groups.
        """
        if not hasattr(user_obj, '_group_perm_cache'):
            group_perms = Permission.objects.filter(group_permissions__members=user_obj
                ).values_list('content_type__app_label', 'codename'
                ).order_by()
            user_obj._group_perm_cache = set(["%s.%s" % (ct, name) for ct, name in group_perms])
        return user_obj._group_perm_cache

    def get_all_permissions(self, user_obj):
        if user_obj.is_anonymous():
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = set([u"%s.%s" % (p.content_type.app_label, p.codename) for p in user_obj.user_permissions.select_related()])
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
        return user_obj._perm_cache
            
    def has_perm(self, user, perm, obj=None):
        # check codename, return false if its a malformed codename
        try:
            perm_type =  perm.split('.')[-1].split('_')[0]
            codename = perm.split('.')[1]
        except IndexError:
            return False
        
        # check group and user permissions, it check the regular users permissions and
        # the custom groups user permissions
        if perm in self.get_all_permissions(user):
            return True
        
        if not obj:
            return False
        
        # object anonymous and use bits
        if perm_type == 'view':
            if obj.allow_anonymous_view:
                return True
            if user.is_authenticated and obj.allow_user_view:
                return True
        if perm_type == 'change':
            if obj.allow_anonymous_edit:
                return True
            if user.is_authenticated and obj.allow_user_edit:
                return True
        
        # no anonymous user currently... TODO: create one?   
        if not user.is_authenticated():
            return False
        
        # check the permissions on the object level
        content_type = ContentType.objects.get_for_model(obj) 
        filters = {
            "content_type": content_type,
            "object_id": obj.pk,
            "codename": codename,
            "user": user
        }
        
        return ObjectPermission.objects.filter(**filters).exists()

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

        
        