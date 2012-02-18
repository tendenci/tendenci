from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

# Abstract base class for authority fields
class TendenciBaseModel(models.Model):    
    # authority fields
    allow_anonymous_view = models.BooleanField(_("Public can view"), default=True)
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

    @property
    def obj_perms(self):
        from perms.fields import has_groups_perms
        t = '<span class="perm-%s">%s</span>'
 
        if self.allow_anonymous_view:
            value = t % ('public','Public')
        elif self.allow_user_view:
            value = t % ('users','Users')
        elif self.allow_member_view:
            value = t % ('members','Members')
        elif has_groups_perms(self):
            value = t % ('groups','Groups')
        else:
            value = t % ('private','Private')

        return mark_safe(value)

    @property
    def obj_status(obj):
        t = '<span class="status-%s">%s</span>'

        if obj.status:
            value = t % (obj.status_detail, obj.status_detail.capitalize())
        else:
            value = t % ('inactive','Inactive')

        return mark_safe(value)

    class Meta:
        abstract = True
