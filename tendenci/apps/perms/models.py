from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.entities.models import Entity
from tendenci.apps.versions.models import Version
from tendenci.apps.categories.models import Category

# Abstract base class for authority fields
class TendenciBaseModel(models.Model):
    # authority fields
    allow_anonymous_view = models.BooleanField(_("Public can view"), default=True)
    allow_user_view = models.BooleanField(_("Signed in user can view"), default=True)
    allow_member_view = models.BooleanField(default=True)
    allow_user_edit = models.BooleanField(_("Signed in user can change"), default=False)
    allow_member_edit = models.BooleanField(default=False)
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
        return self._meta.model_name

    def content_type(self):
        return ContentType.objects.get_for_model(self)

    def content_type_id(self):
        return ContentType.objects.get_for_model(self).pk

    @property
    def obj_perms(self):
        from tendenci.apps.perms.fields import has_groups_perms
        t = '<span class="t-perm t-perm-%s">%s</span>'

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
        t = '<span class="t-status t-status-%s">%s</span>'

        if obj.status:
            if obj.status_detail == 'paid - pending approval':
                value = t % ('pending', obj.status_detail.capitalize())
            else:
                value = t % (obj.status_detail, obj.status_detail.capitalize())
        else:
            value = t % ('inactive', 'Inactive')

        return mark_safe(value)
    
    def get_title(self):
        if hasattr(self, 'meta'):
            return self.get_meta('title')
    
    def get_keywords(self):
        if hasattr(self, 'meta'):
            return self.get_meta('keywords')
    
    def get_description(self):
        if hasattr(self, 'meta'):
            return self.get_meta('description')
    
    def get_canonical_url(self):
        if hasattr(self, 'meta'):
            return self.get_meta('canonical_url')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        with transaction.atomic():
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

        # Soft-delete all base-model objects. This means we
        # set status to False and then save(). We do NOT
        # actually delete anything from the database.
        self.status = False

        # Making slugs unique by appending pk
        # This prevents Integrity errors if
        # an object w/ the same slug is added
        for f in self._meta.fields:
            if 'SlugField' == f.get_internal_type():
                # the length of slug field is 100. make sure the length of modified slug <= 100
                if len(getattr(self, f.name)) + len(str(self.pk)) >= 99:
                    setattr(self, f.name, '%s-%s' % (getattr(self, f.name)[:99-len(str(self.pk))], self.pk))
                else:
                    setattr(self, f.name, '%s-%s' % (getattr(self, f.name), self.pk))

        try:
            self.save(**{'log': False})
        except TypeError:
            self.save()

        # Leave this commented out. We do not want Django to
        # delete our objects from the database.
        # super(TendenciBaseModel, self).delete(*args, **kwargs)

    def hard_delete(self, *args, **kwargs):
        """
        Delete object physically from database
        """
        if self.pk:
            # if status == False, object already be soft-deleted
            if not hasattr(self, 'status') or self.status:
                log = kwargs.get('log', True)
                if log:
                    application = self.__module__
                    EventLog.objects.log(instance=self, application=application)

        # delete object from the database.
        super(TendenciBaseModel, self).delete(*args, **kwargs)

    def update_category_subcategory(self, category_value, subcategory_value):
        category_removed = False
        if not category_value or category_value == '0':
            category_removed = True
            Category.objects.remove(self, 'category')
            Category.objects.remove(self, 'sub_category')
        else:
            Category.objects.update(self, category_value, 'category')

        if not category_removed:
            # update the sub category of this object
            if not subcategory_value or subcategory_value == '0':  # remove
                Category.objects.remove(self, 'sub_category')
            else:
                Category.objects.update(self, subcategory_value, 'sub_category')

