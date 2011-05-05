from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from user_groups.models import Group
from perms.managers import ObjectPermissionManager

# Abstract base class for authority fields
class TendenciBaseModel(models.Model):    
    # authority fields
    allow_anonymous_view = models.BooleanField(_("Public can view"))
    allow_user_view = models.BooleanField(_("Signed in user can view"))
    allow_member_view = models.BooleanField()
    allow_anonymous_edit = models.BooleanField()
    allow_user_edit = models.BooleanField(_("Signed in user can change"))
    allow_member_edit = models.BooleanField()

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="%(class)s_creator", editable=False)
    creator_username = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name="%(class)s_owner")    
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField("Active", default=True)
    status_detail = models.CharField(max_length=50, default='active')

    @property
    def opt_app_label(self):
        return self._meta.app_label

    @property
    def opt_module_name(self):
        return self._meta.module_name
                
    class Meta:
        abstract = True 


class ObjectPermission(models.Model):
    user = models.ForeignKey(User, null=True)
    group = models.ForeignKey('Group', null=True)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField(max_length=255)
    object_id = models.IntegerField()
    create_dt = models.DateTimeField(auto_now_add=True)
    
    objects = ObjectPermissionManager()
