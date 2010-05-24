from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class ObjectPermissionManager(models.Manager):
    def assign(self, user, object, perms=None):
        print 'manager', user
        # check for a list of permissions to pass
        if perms:
            for perm in perms:
                codename = '%s_%s' % (perm, object._meta.object_name.lower())
                content_type = ContentType.objects.get_for_model(object)
                
                perm = Permission.objects.get(codename=codename,
                                              content_type=content_type)
                self.codename = codename
                self.object_id = object.pk
                self.content_type = perm.content_type
                self.user = user
                self.save()
        else:
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
    
    def remove(self, user, object, perms=None):
        # check for a list of permissions to pass
        if perms:
            for perm in perms:
                codename = '%s_%s' % (perm, object._meta.object_name.lower())
                content_type = ContentType.objects.get_for_model(object)
                perm = self.objects.get(codename=codename,
                                        content_type=content_type,
                                        user=user)
                perm.delete()
        else:
            # auto add all the available permissions
            content_type = ContentType.objects.get_for_model(object)
            perms = self.filter(content_type=content_type,
                                        user=user)
            for perm in perms:
                perm.delete()
                    
        