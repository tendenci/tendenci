import re
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from managers import SpeakerManager
from files.models import File

def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    return 'speakers/%s' % (filename)

class Speaker(TendenciBaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=75)
    company = models.CharField(blank=True, max_length=150)
    position = models.CharField(blank=True, max_length=150)
    track = models.CharField(
        max_length=50,
        choices=(
            ('create','Create'),
            ('profit','Profit'),
            ('reach','Reach'),
        ))
    biography = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    order = models.IntegerField(blank=True, max_length=3)

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

    @models.permalink
    def get_absolute_url(self):
        return ("speaker.view", [self.slug])
        
    def professional_photo(self):
        try:
            return self.speakerfile_set.get(photo_type='Professional')
        except:
            return False


class SpeakerFile(File):
    speaker = models.ForeignKey(Speaker)
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
                last = SpeakerFile.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(SpeakerFile, self).save(*args, **kwargs)

    class Meta:
        ordering = ('position',)