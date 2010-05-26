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
        
        # if they outright have the permission from either
        # a group or the user object no reason to hit the database
        if user.has_perm(perm):
            return True

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
        
        # no anonymous user currently... TODO: create one?   
        if not user.is_authenticated():
            return False
        
        content_type = ContentType.objects.get_for_model(obj) 
        filters = {
            "content_type": content_type,
            "object_id": obj.pk,
            "codename": codename,
            "user": user
        }
        
        return ObjectPermission.objects.filter(**filters).exists()
        
        