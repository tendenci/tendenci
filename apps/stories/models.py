import uuid
import re
import os

from parse_uri import ParseUri

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from site_settings.utils import get_setting
from tagging.fields import TagField
from files.models import File, file_directory
from perms.models import TendenciBaseModel
from stories.managers import StoryManager
from entities.models import Entity

# Create your models here.
class Story(TendenciBaseModel):
    """
    A Story is used across a site to add linked image content to a specific design area.
    The basic features of a Story include:
    
    - Title
    - Description (accepts HTML)
    - Image
    - Link
    
    Stories also include tags and a start and end time for automatic expiration.
    
    Stories use the Tendenci Base Model.
    """

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
    image = models.ForeignKey('StoryPhoto', 
        help_text=_('Photo that represents this story.'), null=True, blank=True)
    tags = TagField(blank=True, default='')

    objects = StoryManager()

    class Meta:
        permissions = (("view_story","Can view story"),)
        verbose_name_plural = "stories"

    def __unicode__(self):
        return self.title

    @property
    def content_type(self):
        return 'stories'

    def photo(self):
        if self.image.file:
            return self.image.file

        if self.pk:  # in db
            photo_qs = Story.objects.raw('SELECT id, photo FROM stories_story WHERE id = %s' % self.pk)
            if photo_qs:
                photo = {}
                photo['url'] = photo_qs[0].photo
                return photo

        return None

    def get_absolute_url(self):
        url = self.full_story_link
        parsed_url = ParseUri().parse(url)

        if not parsed_url.protocol:  # if relative URL
            url = '%s%s' % (get_setting('site','global','siteurl'), url)

        return url

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())
        photo_upload = kwargs.pop('photo', None)

        super(Story, self).save(*args, **kwargs)

        if photo_upload and self.pk:
            image = StoryPhoto(
                        creator = self.creator,
                        creator_username = self.creator_username,
                        owner = self.owner,
                        owner_username = self.owner_username
                    )

            image.file.save(photo_upload.name, photo_upload)  # save file row
            image.save()  # save image row

            if self.image: self.image.delete()  # delete image and file row
            self.image = image  # set image

            self.save()

class StoryPhoto(File):
    
    @property
    def content_type(self):
        return 'stories'
    
