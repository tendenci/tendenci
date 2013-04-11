from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from tendenci.core.event_logs.models import EventLog
from tendenci.apps.entities.models import Entity
from tendenci.core.versions.models import Version


# Abstract base class for authority fields
class TendenciBaseModel(models.Model):
    # authority fields
    allow_anonymous_view = models.BooleanField(_("Public can view"), default=True)
    allow_user_view = models.BooleanField(_("Signed in user can view"))
    allow_member_view = models.BooleanField()
    allow_user_edit = models.BooleanField(_("Signed in user can change"))
    allow_member_edit = models.BooleanField()
    entity = models.ForeignKey(Entity, blank=True, null=True, default=None,
        on_delete=models.SET_NULL, related_name="%(app_label)s_%(class)s_entity")
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Last Updated"), auto_now=True)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_creator", editable=False)
    creator_username = models.CharField(max_length=50)
    owner = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_owner")
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField("Active", default=True)
    status_detail = models.CharField(max_length=50, default='active')

    @property
    def opt_app_label(self):
        return self._meta.app_label

    @property
    def opt_module_name(self):
        return self._meta.module_name

    def content_type(self):
        return ContentType.objects.get_for_model(self)

    def content_type_id(self):
        return ContentType.objects.get_for_model(self).pk

    @property
    def obj_perms(self):
        from tendenci.core.perms.fields import has_groups_perms
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
            if obj.status_detail == 'paid - pending approval':
                value = t % ('pending', obj.status_detail.capitalize())
            else:
                value = t % (obj.status_detail, obj.status_detail.capitalize())
        else:
            value = t % ('inactive', 'Inactive')

        return mark_safe(value)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk:
            log = kwargs.get('log', True)
            if log:
                application = self.__module__
                EventLog.objects.log(instance=self, application=application)

            # Save a version of this content.
            try:
                Version.objects.save_version(self.__class__.objects.get(pk=self.pk), self)
            except Exception as e:
                pass
                #print "version error: ", e

        if "log" in kwargs:
            kwargs.pop('log')
        super(TendenciBaseModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.pk:
            log = kwargs.get('log', True)
            if log:
                application = self.__module__
                EventLog.objects.log(instance=self, application=application)
        if "log" in kwargs:
            kwargs.pop('log')
        super(TendenciBaseModel, self).delete(*args, **kwargs)
