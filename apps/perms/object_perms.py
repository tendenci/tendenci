from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from perms.managers import ObjectPermissionManager
from user_groups.models import Group


class ObjectPermission(models.Model):
    user = models.ForeignKey(User, null=True)
    group = models.ForeignKey(Group, null=True)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField(max_length=255)
    object_id = models.IntegerField()
    create_dt = models.DateTimeField(auto_now_add=True)
    
    objects = ObjectPermissionManager()