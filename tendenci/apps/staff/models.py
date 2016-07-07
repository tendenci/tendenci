import re
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tagging.fields import TagField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.staff.managers import StaffManager
from tendenci.apps.files.models import File
from tendenci.apps.files.managers import FileManager
from tendenci.apps.site_settings.models import Setting
from tendenci.libs.abstracts.models import OrderingBaseModel

from django.core.management import call_command
post_save = models.signals.post_save


def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    return 'staff/%s' % (filename)

class Staff(OrderingBaseModel, TendenciBaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=75)
    department = models.ForeignKey('Department', blank=True, null=True)
    positions = models.ManyToManyField('Position', blank=True)
    biography = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)

    cv = models.TextField()

    personal_sites = models.TextField(
        _('Personal Sites'),
        blank=True,
        help_text='List personal websites followed by a return')

    
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = StaffManager()

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (("view_staff","Can view staff"),)
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
        get_latest_by = "-position"
        app_label = 'staff'

    def save(self, *args, **kwargs):
        if self.position is None:
            # Append
            try:
                last = Staff.objects.order_by('-position')[0]
                self.position = last.position + 1
            except (IndexError, TypeError):
                # First row
                self.position = 0

        return super(Staff, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("staff.view", [self.slug])

    def years(self):
        delta = datetime.now().date() - self.start_date
        years = abs(round((delta.days / (365.25)), 2))
        return years
        
    def featured_photo(self):
        try:
            return self.stafffile_set.get(photo_type='Featured')
        except:
            return False

class Department(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        app_label = 'staff'

    def __unicode__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        app_label = 'staff'

    def __unicode__(self):
        return self.name


class StaffFile(OrderingBaseModel, File):

    PHOTO_TYPE_FEATURED = 'featured'
    PHOTO_TYPE_OTHER = 'featured'

    PHOTO_TYPE_CHOICES = (
        (PHOTO_TYPE_FEATURED,'Featured'),
        (PHOTO_TYPE_OTHER, 'Other'),
    )

    staff = models.ForeignKey(Staff)
    photo_type = models.CharField(
        max_length=50,
        choices=PHOTO_TYPE_CHOICES
        )

    objects = FileManager()

    def save(self, *args, **kwargs):
        if self.position is None:
            # Append
            try:
                last = StaffFile.objects.order_by('-position')[0]
                last.position = last.position or 0
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(StaffFile, self).save(*args, **kwargs)

    class Meta:
        ordering = ('position',)
        app_label = 'staff'
        
def post_save_setting(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance and instance.name=='staff_url':
        call_command('clear_cache')

post_save.connect(post_save_setting, sender=Setting)
