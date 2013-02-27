from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from timezones.fields import TimeZoneField

from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.object_perms import ObjectPermission

# Abstract base class for authority fields
class TendenciBaseModel(models.Model):
    # authority fields
    allow_anonymous_view = models.BooleanField(_("Public can view"), default=True)
    allow_user_view = models.BooleanField(_("Signed in user can view"))
    allow_member_view = models.BooleanField()
    allow_user_edit = models.BooleanField(_("Signed in user can change"))
    allow_member_edit = models.BooleanField()

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_creator", editable=False)
    creator_username = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner")
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField("Active", default=True)
    status_detail = models.CharField(max_length=50, default='active')

    class Meta:
        abstract = True

    @property
    def opt_app_label(self):
        return self._meta.app_label

    @property
    def opt_module_name(self):
        return self._meta.module_name

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


class Person(TendenciBaseModel):
    user = models.OneToOneField(User, related_name="profile", verbose_name=_('user'))
    phone = models.CharField(_('phone'), max_length=50, blank=True)
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, default='', blank=True)
    member_number = models.CharField(_('member number'), max_length=50, blank=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zipcode = models.CharField(_('zipcode'), max_length=50, blank=True)
    county = models.CharField(_('county'), max_length=50, blank=True)
    country = models.CharField(_('country'), max_length=50, blank=True)

    url = models.CharField(_('url'), max_length=100, blank=True)

    time_zone = TimeZoneField(_('timezone'))
    language = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    perms = generic.GenericRelation(ObjectPermission,
        object_id_field="object_id", content_type_field="content_type")

    class Meta:
        abstract = True


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
