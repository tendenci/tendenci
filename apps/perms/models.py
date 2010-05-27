from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from usergroups.models import Group


from perms.managers import ObjectPermissionManager

class ObjectPermission(models.Model):
    user = models.ForeignKey(User, null=True)
    group = models.ForeignKey(Group, null=True)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField(max_length=255)
    object_id = models.IntegerField()
    create_dt = models.DateTimeField(auto_now_add=True)
    
    objects = ObjectPermissionManager()
    