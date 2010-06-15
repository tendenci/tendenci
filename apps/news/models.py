import uuid
from django.db import models
from tagging.fields import TagField
from timezones.fields import TimeZoneField
from perms.models import AuditingBaseModel
from news.managers import NewsManager

class News(AuditingBaseModel):
    guid = models.CharField(max_length=200, default=uuid.uuid1)
    timezone = TimeZoneField()
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    source = models.CharField(max_length=300, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)
    release_dt = models.DateTimeField(null=True, blank=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    syndicate = models.BooleanField()
    design_notes = models.TextField(blank=True)
    enclosure_url = models.CharField(max_length=500, blank=True) # for podcast feeds
    enclosure_type = models.CharField(max_length=120, blank=True) # for podcast feeds
    enclosure_length = models.IntegerField(default=0) # for podcast feeds
    useautotimestamp = models.BooleanField()
    tags = TagField(blank=True)

    objects = NewsManager()
    class Meta:
        permissions = (("view_news","Can view news"),)
        verbose_name_plural = "news"

    @models.permalink
    def get_absolute_url(self):
        return ("news", [self.pk])

    def __unicode__(self):
        return self.headline