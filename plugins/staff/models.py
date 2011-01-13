import re
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from managers import StaffManager

def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    return 'staff/%s' % (filename)

class Staff(TendenciBaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=75)
    department = models.ForeignKey('Department', blank=True, null=True)
    position = models.ForeignKey('Position',  blank=True, null=True)
    start_date = models.DateField()
    biography = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    photo = models.ImageField(max_length=260, upload_to=file_directory,
                             help_text=_('Employee Photo. Only valid images.'),
                             blank=True)
    
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))

    objects = StaffManager()

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (("view_staff","Can view staff"),)
        verbose_name = 'staff'
        verbose_name_plural = 'staff'
        get_latest_by = "start_date"

    @models.permalink
    def get_absolute_url(self):
        return ("staff.view", [self.slug])

    def years(self):
        delta = datetime.now().date() - self.start_date
        years = abs(round((delta.days / (365.25)), 2))
        return years

class Department(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name