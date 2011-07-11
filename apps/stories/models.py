import uuid
import re
from parse_uri import ParseUri

from django.db import models
from django.utils.translation import ugettext_lazy as _
from site_settings.utils import get_setting
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from stories.managers import StoryManager
from entities.models import Entity


def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    return 'stories/%s' % (filename)

# Create your models here.
class Story(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    syndicate = models.BooleanField(_('Include in RSS feed'))
    full_story_link = models.CharField(_('Full Story Link'), max_length=300, blank=True)
    start_dt = models.DateTimeField(_('Start Date/Time'), null=True, blank=True)
    end_dt = models.DateTimeField(_('End Date/Time'), null=True, blank=True)
    expires = models.BooleanField(_('Expires'), default=True)
    ncsortorder = models.IntegerField(null=True, blank=True)
    entity = models.ForeignKey(Entity,null=True)
    photo = models.FileField(max_length=260, upload_to=file_directory, 
        help_text=_('Photo that represents this story.'), null=True, blank=True)
    tags = TagField(blank=True, default='')

    objects = StoryManager()
    
    class Meta:
        permissions = (("view_story","Can view story"),)
        verbose_name_plural = "stories"
        
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            
        super(Story, self).save(*args, **kwargs)

    def get_absolute_url(self):
        url = self.full_story_link
        parsed_url = ParseUri().parse(url)

        if not parsed_url.protocol:  # if relative URL
            url = '%s%s' % (get_setting('site','global','siteurl'), url)

        return url

    def __unicode__(self):
        return self.title