from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from tendenci.core.perms.managers import ObjectPermissionManager
from tendenci.apps.user_groups.models import Group


class ObjectPermission(models.Model):
    """
    Object level permissions

    Don't move this model into the models.py
    because it will cause circular references
    all over the place. Please leave it here.
    """
    user = models.ForeignKey(User, null=True)
    group = models.ForeignKey(Group, null=True)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField(max_length=255)
    object_id = models.IntegerField()
    create_dt = models.DateTimeField(auto_now_add=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    objects = ObjectPermissionManager()
