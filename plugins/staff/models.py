import re
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from perms.object_perms import ObjectPermission
from managers import StaffManager
from files.models import File
from site_settings.models import Setting

from django.core.management import call_command
post_save = models.signals.post_save

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

    facebook = models.CharField(blank=True, max_length=100)
    twitter = models.CharField(blank=True, max_length=100)
    linkedin = models.CharField(blank=True, max_length=100)
    get_satisfaction = models.CharField('GetSatisfaction', blank=True, max_length=100)
    flickr = models.CharField(blank=True, max_length=100)
    slideshare = models.CharField(blank=True, max_length=100)

    cv = models.TextField()
    tiny_bio = models.CharField('5 second bio', blank=True, max_length=140, help_text=_('140 characters max.'))

    question = models.CharField(blank=True, max_length=150)
    answer = models.TextField(blank=True)

    personal_sites = models.TextField(
        _('Personal Sites'),
        blank=True,
        help_text='List personal websites followed by a return')

    
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = StaffManager()

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (("view_staff","Can view staff"),)
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
        get_latest_by = "-start_date"

    @models.permalink
    def get_absolute_url(self):
        return ("staff.view", [self.slug])

    def years(self):
        delta = datetime.now().date() - self.start_date
        years = abs(round((delta.days / (365.25)), 2))
        return years
        
    def professional_photo(self):
        try:
            return self.stafffile_set.get(photo_type='Professional')
        except:
            return False

class Department(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class StaffFile(File):
    staff = models.ForeignKey(Staff)
    photo_type = models.CharField(
        max_length=50,
        choices=(
            ('polaroid','Polaroid'),
            ('professional','Professional'),
            ('fun','Fun'),
            ('other','Other'),
        ))
    position = models.IntegerField(blank=True)

    def save(self, *args, **kwargs):
        if self.position is None:
            # Append
            try:
                last = StaffFile.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(StaffFile, self).save(*args, **kwargs)

    class Meta:
        ordering = ('position',)
        
def post_save_setting(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance and instance.name=='staff_url':
        call_command('touch_settings')

post_save.connect(post_save_setting, sender=Setting)
