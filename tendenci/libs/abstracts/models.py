from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.event_logs.models import EventLog


# Abstract base class for authority fields
class TendenciBaseModel(models.Model):
    # authority fields
    allow_anonymous_view = models.BooleanField(_("Public can view"), default=False)
    allow_user_view = models.BooleanField(_("Signed in user can view"), default=False)
    allow_member_view = models.BooleanField(default=False)
    allow_user_edit = models.BooleanField(_("Signed in user can change"), default=False)
    allow_member_edit = models.BooleanField(default=False)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_creator", editable=False, on_delete=models.CASCADE)
    creator_username = models.CharField(max_length=150)
    owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner" , on_delete=models.CASCADE)
    owner_username = models.CharField(max_length=150)
    status = models.BooleanField("Active", default=True)
    status_detail = models.CharField(max_length=50, default='active')

    class Meta:
        abstract = True

    @property
    def opt_app_label(self):
        return self._meta.app_label

    @property
    def opt_module_name(self):
        return self._meta.model_name

    @property
    def obj_perms(self):
        from tendenci.apps.perms.fields import has_groups_perms
        t = '<span class="t-profile-perm t-perm-%s">%s</span>'

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
        t = '<span class="t-profile-status t-status-%s">%s</span>'

        if obj.status:
            if obj.status_detail == 'paid - pending approval':
                value = t % ('pending', obj.status_detail.capitalize())
            else:
                value = t % (obj.status_detail, obj.status_detail.capitalize())
        else:
            value = t % ('inactive','Inactive')

        return mark_safe(value)

    def save(self, *args, **kwargs):
        if self.pk:
            log = kwargs.get('log', True)
            if log:
                application = self.__module__
                EventLog.objects.log(instance=self, application=application)
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


class UnsavedOneToOne(models.OneToOneField):
    # A ForeignKey which can point to an unsaved object
    allow_unsaved_instance_assignment = True


class Address(models.Model):
    """
    The same set of fields that comes with a typical address
    """
    address = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=50, blank=True)
    county = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)

    class Meta:
        abstract = True


class Identity(models.Model):
    """
    First name, last name, and email address
    """
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        abstract = True


class OrderingBaseModel(models.Model):
    position = models.IntegerField(_('Position'), default=0,
                                   null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ('position',)
