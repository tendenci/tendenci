import re

from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.speakers.managers import SpeakerManager
from tendenci.apps.files.models import File
from tendenci.apps.files.managers import FileManager


def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    return 'speakers/%s' % (filename)

class Track(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        app_label = 'speakers'

    def __unicode__(self):
        return self.name

class Speaker(TendenciBaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=75)
    company = models.CharField(blank=True, max_length=150)
    position = models.CharField(blank=True, max_length=150)
    track = models.ForeignKey(Track, null=True)
    biography = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    ordering = models.IntegerField(_('order'))

    facebook = models.CharField(blank=True, max_length=100)
    twitter = models.CharField(blank=True, max_length=100)
    linkedin = models.CharField(blank=True, max_length=100)
    get_satisfaction = models.CharField('GetSatisfaction', blank=True, max_length=100)
    flickr = models.CharField(blank=True, max_length=100)
    slideshare = models.CharField(blank=True, max_length=100)


    personal_sites = models.TextField(
        _('Personal Sites'),
        blank=True,
        help_text='List personal websites followed by a return')

    
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))

    objects = SpeakerManager()

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (("view_speaker","Can view speaker"),)
        verbose_name = 'speaker'
        verbose_name_plural = 'speaker'
        get_latest_by = "-start_date"
        app_label = 'speakers'

    @models.permalink
    def get_absolute_url(self):
        return ("speaker.view", [self.slug])
        
    def professional_photo(self):
        try:
            return self.speakerfile_set.filter(photo_type__iexact='professional')[0]
        except:
            return False
    
    def fun_photo(self):
        try:
            return self.speakerfile_set.filter(photo_type__iexact='fun')[0]
        except:
            return False


class SpeakerFile(File):
    speaker = models.ForeignKey(Speaker)
    photo_type = models.CharField(
        max_length=50,
        choices=(
            ('professional','Professional'),
            ('fun','Fun'),
        ))
    position = models.IntegerField(blank=True)

    objects = FileManager()

    def save(self, *args, **kwargs):
        if self.position is None:
            # Append
            try:
                last = SpeakerFile.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(SpeakerFile, self).save(*args, **kwargs)

    class Meta:
        ordering = ('position',)
        app_label = 'speakers'
