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
        if instance.allow_anonymous_edit:
            return True
        return False
    
    def allow_user_edit(self, instance):
        if instance.allow_user_edit:
            if isinstance(self.user,AnonymousUser):
                return False
        return False

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
    
    def edit(self):
        auth = False
        check_edit = eval('self.check.change_%s' % (self.object_name,),
                          self.globals, self.locals)
        if self.instance:
            if self.check.allow_anonymous_edit(self.instance):
                auth = True
            elif self.check.allow_user_edit(self.instance):
                auth = True
            elif check_edit(self.instance):
                auth = True
        else:
            if check_edit():
                auth = True
        
        return auth
    
    def delete(self):
        auth = False
        check_delete = eval('self.check.delete_%s' % (self.object_name,),
                          self.globals, self.locals)

        if self.instance:
            if check_delete(self.instance):
                auth = True            
        else:
            if check_delete():
                auth = True
                     
        return auth
    
    def add(self):
        auth = False
        check_add = eval('self.check.add_%s' % (self.object_name,),
                          self.globals, self.locals)
        
        if self.instance:
            if check_add(self.instance):
                auth = True            
        else:
            if check_add():
                auth = True
        
        return auth
    
    