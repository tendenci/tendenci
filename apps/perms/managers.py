from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class ObjectPermissionManager(models.Manager):
    def assign(self, user_or_users, object, perms=None):
        """
            Assigns permissions to user or multiple users
            assign(self, user_or_users, object, perms=None)
            
            user_or_users can be a single users object, list, or queryset
            object is the instance of a model
            perms are if you want to assign individual permissions
            ie. ['change','add','view']
        """
        multi_user = False
        
        if isinstance(user_or_users,list):
            multi_user = True
        if isinstance(user_or_users,QuerySet):
            multi_user = True
        
        # add permissions based on list of permissions passed
        if perms:
            if multi_user:
                for user in user_or_users:
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
            else:
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
        else:
            if multi_user:
                for user in user_or_users:
                    # auto add all the available permissions
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
            else:
                # auto add all the available permissions
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
            
    def remove(self, user_or_users, object, perms=None):
        """
            Remove permissions to user or multiple users
            remove(self, user_or_users, object, perms=None)
            
            user_or_users can be a single users object, list, or queryset
            object is the instance of a model
            perms are if you want to remove individual permissions
            ie. ['change','add','view']
        """
        multi_user = False
        
        if isinstance(user_or_users,list):
            multi_user = True
        if isinstance(user_or_users,QuerySet):
            multi_user = True
            
        if perms:
            if multi_user:
                for user in user_or_users:
                    for perm in perms:
                        codename = '%s_%s' % (perm, object._meta.object_name.lower())
                        content_type = ContentType.objects.get_for_model(object)
                        perm = self.objects.get(codename=codename,
                                                content_type=content_type,
                                                object_id=object.pk,
                                                user=user)
                        perm.delete()                 
            else:
                for perm in perms:
                    codename = '%s_%s' % (perm, object._meta.object_name.lower())
                    content_type = ContentType.objects.get_for_model(object)
                    perm = self.objects.get(codename=codename,
                                            content_type=content_type,
                                            object_id=object.pk,
                                            user=user_or_users)
                    perm.delete()
        else:
            if multi_user:
                for user in user_or_users:
                    content_type = ContentType.objects.get_for_model(object)
                    perms = self.filter(content_type=content_type,
                                        object_id=object.pk,
                                        user=user)
                    for perm in perms:
                        perm.delete()
            else:
                content_type = ContentType.objects.get_for_model(object)
                perms = self.filter(content_type=content_type,
                                    object_id=object.pk,
                                    user=user_or_users)
                for perm in perms:
                    perm.delete()              
                    
        