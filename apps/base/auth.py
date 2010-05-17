from django.contrib.auth.models import AnonymousUser

from authority import permissions

class BasePermission(permissions.BasePermission):
    """
        Permissions for articles
    """
    checks = ('view', 'allow_anonymous_view', 'allow_user_view',
              'allow_anonymous_edit','allow_user_edit')
    
    # anyone can view this 
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
        pass
    
    def allow_user_edit(self, instance):
        pass

class Authorize(object):
    """ authorization class for tendenci """
    def __init__(self, user, check_class, instance=None):
        self.user = user
        self.check = check_class(self.user)
        self.instance = instance
        self.object_name = self.check.model._meta.object_name.lower()
        
        # for eval function security
        self.globals = {"__builtins__": None}
        self.locals = {'self': self}
        
    def view(self):
        auth = False
        check_view = eval('self.check.view_%s' % (self.object_name,),
                          self.globals, self.locals)
        if self.instance:
            if self.check.allow_anonymous_view(self.instance):
                auth = True
            elif self.check.allow_user_view(self.instance):
                auth = True
            elif check_view(self.instance):
                auth = True
        else:
            if check_view():
                auth = True
        
        return auth
    
    def change(self):
        pass
    
    def delete(self):
        pass
    
    def add(self):
        pass
    
    