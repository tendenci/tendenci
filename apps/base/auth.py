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
    checks = ('view', 'allow_anonymous_view', 'allow_user_view',
              'allow_anonymous_edit','allow_user_edit')

    def __init__(self, user=None, group=None, *args, **kwargs):
        super(BasePermission, self).__init__(user=user, group=group, *args, **kwargs)
        
        # for eval function security
        self.object_name = self.model._meta.object_name.lower()
        self.globals = {"__builtins__": None}
        self.locals = {'self': self}

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
    
    # check curry functions
    def allow_anonymous_view(self, instance):
        if instance.allow_anonymous_view:
            return True
        return False
    
    def allow_user_view(self, instance):
        if instance.allow_user_view:
            if isinstance(self.user,AnonymousUser):
                return False
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
        
    # Main tendenci permissions, new function
    def view(self, instance=None):
        auth = False
        check_view = eval('self.view_%s' % (self.object_name,),
                          self.globals, self.locals)
        if instance:
            if self.allow_anonymous_view(instance):
                auth = True
            elif self.allow_user_view(instance):
                auth = True
            elif check_view(instance):
                auth = True
        else:
            if check_view():
                auth = True
        
        return auth
    
    def edit(self, instance=None):
        auth = False
        check_edit = eval('self.change_%s' % (self.object_name,),
                          self.globals, self.locals)
        if instance:
            if self.allow_anonymous_edit(instance):
                auth = True
            elif self.allow_user_edit(instance):
                auth = True
            elif check_edit(instance):
                auth = True
        else:
            if check_edit():
                auth = True
        
        return auth
    
    def delete(self, instance=None):
        auth = False
        check_delete = eval('self.delete_%s' % (self.object_name,),
                          self.globals, self.locals)

        if instance:
            if check_delete(instance):
                auth = True            
        else:
            if check_delete():
                auth = True
                     
        return auth
    
    def add(self, instance=None):
        auth = False
        check_add = eval('self.add_%s' % (self.object_name,),
                          self.globals, self.locals)
        
        if instance:
            if check_add(instance):
                auth = True            
        else:
            if check_add():
                auth = True
        
        return auth
            

        
    
    
    