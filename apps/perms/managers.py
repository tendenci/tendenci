from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class ObjectPermissionManager(models.Manager):
    def who_has_perm(self, perm, instance):
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
                    users.append(perm.user)
            
                if perm.group:
                    for user in perm.group.members.all():
                        users.append(user)
            return list(set(users))
        else:
            return None

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
        if not isinstance(perms,list):
            perms = None
        # check for multi_groups
        if isinstance(group_or_groups,list):
            multi_group = True
        if isinstance(group_or_groups,QuerySet):
            multi_group = True
        if isinstance(group_or_groups,tuple):
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
                    "codename":codename,
                    "object_id":object.pk,
                    "content_type":perm.content_type,
                    "group": group,    
                }
                self.get_or_create(**defaults)  
            return # get out
                                        
        if multi_group:
            for group in group_or_groups:
                if perms:
                    for perm in perms:
                        codename = '%s_%s' % (perm, object._meta.object_name.lower())
                        content_type = ContentType.objects.get_for_model(object)
                        
                        perm = Permission.objects.get(codename=codename,
                                                      content_type=content_type)
                        
                        defaults = {
                            "codename":codename,
                            "object_id":object.pk,
                            "content_type":perm.content_type,
                            "group": group,    
                        }
                        self.get_or_create(**defaults)     
                else:  # all default permissions
                    content_type = ContentType.objects.get_for_model(object)
                    perms = Permission.objects.filter(content_type=content_type)
                    for perm in perms:
                        defaults = {
                            "codename":perm.codename,
                            "object_id":object.pk,
                            "content_type":content_type,
                            "group":group,    
                        }
                        self.get_or_create(**defaults)                                      
        else: # not multi_group
            if perms:
                for perm in perms:
                    codename = '%s_%s' % (perm, object._meta.object_name.lower())
                    content_type = ContentType.objects.get_for_model(object)
                    
                    perm = Permission.objects.get(codename=codename,
                                                  content_type=content_type)
                    defaults = {
                        "codename":codename,
                        "object_id":object.pk,
                        "content_type":perm.content_type,
                        "group": group_or_groups,    
                    }
                    self.get_or_create(**defaults) 
            else:  # all default permissions
                content_type = ContentType.objects.get_for_model(object)
                perms = Permission.objects.filter(content_type=content_type)
                for perm in perms:
                    defaults = {
                        "codename":perm.codename,
                        "object_id":object.pk,
                        "content_type":content_type,
                        "group":group_or_groups,
                                
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
        if not isinstance(perms,list):
            perms = None        
        # check for multi_users
        if isinstance(user_or_users,list):
            multi_user = True
        if isinstance(user_or_users,QuerySet):
            multi_user = True
        if isinstance(user_or_users,tuple):
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
                            "codename":codename,
                            "object_id":object.pk,
                            "content_type":perm.content_type,
                            "user":user,    
                        }
                        self.get_or_create(**defaults)
                else:  # all default permissions
                    content_type = ContentType.objects.get_for_model(object)
                    perms = Permission.objects.filter(content_type=content_type)
                    for perm in perms:
                        defaults = {
                            "codename":perm.codename,
                            "object_id":object.pk,
                            "content_type":content_type,
                            "user":user,
                                    
                        }
                        self.get_or_create(**defaults)                       
        else: # not muli_user
            if perms:
                for perm in perms:
                    codename = '%s_%s' % (perm, object._meta.object_name.lower())
                    content_type = ContentType.objects.get_for_model(object)
                    
                    perm = Permission.objects.get(codename=codename,
                                                  content_type=content_type)
                    defaults = {
                        "codename":codename,
                        "object_id":object.pk,
                        "content_type":perm.content_type,
                        "user":user_or_users,    
                    }
                    self.get_or_create(**defaults) 
            else: # all default permissions
                content_type = ContentType.objects.get_for_model(object)
                perms = Permission.objects.filter(content_type=content_type)
                for perm in perms:
                    defaults = {
                        "codename":perm.codename,
                        "object_id":object.pk,
                        "content_type":content_type,
                        "user":user_or_users,
                                
                    }
                    self.get_or_create(**defaults)                                    
    
    def remove_all(self, object):
        """
            Remove all permissions on object (instance)
        """
        content_type = ContentType.objects.get_for_model(object)
        perms = self.filter(content_type=content_type,
                            object_id=object.pk)
        for perm in perms:
            perm.delete()          

# the function below were removed cause they were not needed as of yet. 
# They need to be updated and tested
            
#    def remove_group(self, group_or_groups, object, perms=None):
#        """
#            Remove permissions to group or multiple groups
#            assign_group(self, group_or_groups, object, perms=None)
#            
#            -- group_or_groups: can be a single group object, list, queryset
#            or tuple.
#            
#            -- object: is the instance of a model class
#            
#            -- perms: a list of individual permissions to assign to each group
#               leave blank for all permissions.
#        """    
#        multi_group = False
#        
#        if isinstance(group_or_groups,list):
#            multi_group = True
#        if isinstance(group_or_groups,QuerySet):
#            multi_group = True
#        if isinstance(group_or_groups,tuple):
#            multi_group = True
#                        
#        
#        if multi_group:
#            for group in group_or_groups:
#                if perms:
#                    for perm in perms:
#                        codename = '%s_%s' % (perm, object._meta.object_name.lower())
#                        content_type = ContentType.objects.get_for_model(object)
#                        perm = self.objects.get(codename=codename,
#                                                content_type=content_type,
#                                                object_id=object.pk,
#                                                group=group)
#                        perm.delete()                 
#                else: 
#                    content_type = ContentType.objects.get_for_model(object)
#                    perms = self.filter(content_type=content_type,
#                                        object_id=object.pk,
#                                        group=group)
#                    for perm in perms:
#                        perm.delete()        
#        else:
#            if perms:
#                for perm in perms:
#                    codename = '%s_%s' % (perm, object._meta.object_name.lower())
#                    content_type = ContentType.objects.get_for_model(object)
#                    perm = self.objects.get(codename=codename,
#                                            content_type=content_type,
#                                            object_id=object.pk,
#                                            group=group_or_groups)
#                    perm.delete()
#            else:
#                content_type = ContentType.objects.get_for_model(object)
#                perms = self.filter(content_type=content_type,
#                                    object_id=object.pk,
#                                    group=group_or_groups)
#                for perm in perms:
#                    perm.delete()             
#        
#    def remove(self, user_or_users, object, perms=None):
#        """
#            Remove permissions to user or multiple users
#            remove(self, user_or_users, object, perms=None)
#            
#            user_or_users can be a single users object, list, or queryset
#            object is the instance of a model
#            perms are if you want to remove individual permissions
#            ie. ['change','add','view']
#        """
#        multi_user = False
#        
#        
#        if isinstance(user_or_users,list):
#            multi_user = True
#        if isinstance(user_or_users,QuerySet):
#            multi_user = True
#            
#        if perms:
#            if multi_user:
#                for user in user_or_users:
#                    for perm in perms:
#                        codename = '%s_%s' % (perm, object._meta.object_name.lower())
#                        content_type = ContentType.objects.get_for_model(object)
#                        perm = self.objects.get(codename=codename,
#                                                content_type=content_type,
#                                                object_id=object.pk,
#                                                user=user)
#                        perm.delete()                 
#            else:
#                for perm in perms:
#                    codename = '%s_%s' % (perm, object._meta.object_name.lower())
#                    content_type = ContentType.objects.get_for_model(object)
#                    perm = self.objects.get(codename=codename,
#                                            content_type=content_type,
#                                            object_id=object.pk,
#                                            user=user_or_users)
#                    perm.delete()
#        else:
#            if multi_user:
#                for user in user_or_users:
#                    content_type = ContentType.objects.get_for_model(object)
#                    perms = self.filter(content_type=content_type,
#                                        object_id=object.pk,
#                                        user=user)
#                    for perm in perms:
#                        perm.delete()
#            else:
#                content_type = ContentType.objects.get_for_model(object)
#                perms = self.filter(content_type=content_type,
#                                    object_id=object.pk,
#                                    user=user_or_users)
#                for perm in perms:
#                    perm.delete()              
                    
        