from django.db import models

from tagging.fields import TagField
from timezones.fields import TimeZoneField

from perms.models import AuditingBaseModel
from articles.managers import ArticleManager

class Article(AuditingBaseModel):

    # TODO: make unique=True (dependent on migration script)
    guid = models.CharField(max_length=50, unique=False, blank=True)
    timezone = TimeZoneField()
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    source = models.CharField(max_length=300, blank=True)

    # creator first name and lastname
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)

    # release dates do not have to be set
    release_dt = models.DateTimeField(null=True, blank=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    syndicate = models.BooleanField()

    # TODO: might go away with tags
    featured = models.BooleanField()
    design_notes = models.TextField(blank=True)

    tags = TagField(blank=True)

    # for podcast feeds
    enclosure_url = models.CharField(max_length=500, blank=True)
    enclosure_type = models.CharField(max_length=120, blank=True)
    enclosure_length = models.IntegerField(default=0)

    not_official_content = models.BooleanField(blank=True)

    # meta information
    page_title = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)

    objects = ArticleManager()

    class Meta:
        permissions = (("view_article","Can view article"),)

    @models.permalink
    def get_absolute_url(self):
        return ("article", [self.pk])

    def __unicode__(self):
        return self.headline


