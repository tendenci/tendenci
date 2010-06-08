from django.db import models

from perms.models import AuditingBaseModel
from stories.managers import StoryManager

# Create your models here.
class Story(AuditingBaseModel):
    guid = models.CharField(max_length=50, unique=False, blank=True)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    syndicate = models.BooleanField()
    create_dt = models.DateTimeField(auto_now_add=True)
    fullstorylink = models.CharField(max_length=300, blank=True)
    start_dt = models.DateTimeField(null=True, blank=True)
    end_dt = models.DateTimeField(null=True, blank=True)
    ncsortorder = models.IntegerField(null=True, blank=True)
 
    objects = StoryManager()
    
    class Meta:
        permissions = (("view_story","Can view story"),)
        verbose_name_plural = "stories"

    def get_absolute_url(self):
        return ('story', [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)
               
    def __unicode__(self):
        return self.title
        