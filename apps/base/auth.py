from django.contrib.auth.models import AnonymousUser
from django.db.models.base import Model, ModelBase
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from authority import permissions
from authority.exceptions import NotAModel, UnsavedModelInstance
from authority.models import Permission

class BasePermission(permissions.BasePermission):
    """
        Permissions for articles
    """
    checks = ('view', 'edit', 'delete', 'add')

    def __init__(self, user=None, group=None, *args, **kwargs):
        super(BasePermission, self).__init__(user=user, group=group, *args, **kwargs)
        
        # for eval function security
        self.app_label = self.model._meta.app_label.lower()
        self.object_name = self.model._meta.object_name.lower()

    def remove(self, check=None, content_object=None, generic=False):
        """
        Remove a permission to a user.

        To remove permission for all checks: let check=None.
        To remove permission for all objects: let content_object=None.

        If generic is True then "check" will be suffixed with _modelname.
        """
        result = []

        if not content_object:
            content_objects = (self.model,)
        elif not isinstance(content_object, (list, tuple)):
            content_objects = (content_object,)
        else:
            content_objects = content_object

        if not check:
            checks = self.generic_checks + getattr(self, 'checks', [])
        elif not isinstance(check, (list, tuple)):
            checks = (check,)
        else:
            checks = check

        for content_object in content_objects:
            # raise an exception before adding any permission
            # i think Django does not rollback by default
            if not isinstance(content_object, (Model, ModelBase)):
                raise NotAModel(content_object)
            elif isinstance(content_object, Model) and not content_object.pk:
                raise UnsavedModelInstance(content_object)

            content_type = ContentType.objects.get_for_model(content_object)

            for check in checks:
                if isinstance(content_object, Model):
                    # make an authority per object permission
                    codename = self.get_codename(check, content_object, generic)
                    try:
                        perm = Permission.objects.get(
                            user = self.user,
                            codename = codename,
                            approved = True,
                            content_type = content_type,
                            object_id = content_object.pk)
                    
                        perm.delete()
                        result.append(perm)
                    except ObjectDoesNotExist:
                        pass

        return result
        
    # Main tendenci permissions, new function
    def allow_anonymous_view(self, instance):
        if instance.allow_anonymous_view:
            return True
        return False
    
    def allow_user_view(self, instance):
        if instance.allow_user_view:
            if isinstance(self.user,AnonymousUser):
                return False
            else:
                return True
        return False

    def allow_anonymous_edit(self, instance):
        if instance.allow_anonymous_edit:
            return True
        return False
    
    def allow_user_edit(self, instance):
        if instance.allow_user_edit:
            if isinstance(self.user,AnonymousUser):
                return False
        return False
    
    def view(self, instance=None):
        auth = False
        if instance:
            if self.allow_anonymous_view(instance):
                auth = True
            elif self.allow_user_view(instance):
                auth = True
            elif self.user.has_perm("%s.%s" % (self.app_label, 'view_%s' % self.object_name)):
                auth = True
            elif self.can('view', instance):
                auth = True
        else:
            if self.user.has_perm("%s.%s" % (self.app_label, 'view_%s' % self.object_name)):
                auth = True
        
        return auth
    
    def edit(self, instance=None):
        auth = False
        if instance:
            if self.allow_anonymous_edit(instance):
                auth = True
            elif self.allow_user_edit(instance):
                auth = True
            elif self.user.has_perm("%s.%s" % (self.app_label, 'change_%s' % self.object_name)):
                auth = True
            elif self.can('edit', instance):
                auth = True
        else:
            if self.user.has_perm("%s.%s" % (self.app_label, 'change_%s' % self.object_name)):
                auth = True
        
        return auth
    
    def delete(self, instance=None):
        auth = False
        if instance:
            if self.user.has_perm("%s.%s" % (self.app_label, 'delete_%s' % self.object_name)):
                auth = True
            elif self.can('delete', instance):
                auth = True          
        else:
            if self.user.has_perm("%s.%s" % (self.app_label, 'delete_%s' % self.object_name)):
                auth = True
                     
        return auth
    
    def add(self, instance=None):
        auth = False        
        if instance:
            if self.user.has_perm("%s.%s" % (self.app_label, 'add_%s' % self.object_name)):
                auth = True
            elif self.can('add', instance):
                auth = True          
        else:
            if self.user.has_perm("%s.%s" % (self.app_label, 'add_%s' % self.object_name)):
                auth = True
        
        return auth
            

        
    
    
    