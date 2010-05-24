from django.contrib.contenttypes.models import ContentType
from perms.models import ObjectPermission

class ObjectPermBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        return None
        
    def has_perm(self, user, perm, obj=None):
        # let the ModelBackend handle this one
        if obj is None:
            return False

        content_type = ContentType.objects.get_for_model(obj)

        try:
            perm_type =  perm.split('.')[-1].split('_')[0]
            codename = perm.split('.')[1]
        except IndexError:
            return False
        
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
            
        filters = {
            "content_type": content_type,
            "object_id": obj.pk,
            "codename": codename,
            "user": user
        }
        
        print filters
        
        return ObjectPermission.objects.filter(**filters).exists()
        
        