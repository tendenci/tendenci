from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from perms.managers import ObjectPermissionManager

class ObjectPermission(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField(max_length=255)
    object_id = models.IntegerField()
    create_dt = models.DateTimeField(auto_now_add=True)
    
    objects = ObjectPermissionManager()
    