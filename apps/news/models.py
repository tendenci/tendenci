import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from timezones.fields import TimeZoneField
from perms.models import AuditingBaseModel
from news.managers import NewsManager
from tinymce import models as tinymce_models

class News(AuditingBaseModel):
    guid = models.CharField(max_length=40, default=uuid.uuid1)
    timezone = TimeZoneField(_('Time Zone'))
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)

    body = tinymce_models.HTMLField()

    source = models.CharField(max_length=300, blank=True)
    first_name = models.CharField(_('First Name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)
    release_dt = models.DateTimeField(_('Release Date/Time'), null=True, blank=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    syndicate = models.BooleanField(_('Include in RSS feed'))
    design_notes = models.TextField(_('Design Notes'), blank=True)
    enclosure_url = models.CharField(_('Enclosure URL'), max_length=500, blank=True) # for podcast feeds
    enclosure_type = models.CharField(_('Enclosure Type'),max_length=120, blank=True) # for podcast feeds
    enclosure_length = models.IntegerField(_('Enclosure Length'), default=0) # for podcast feeds
    useautotimestamp = models.BooleanField(_('Auto Timestamp'))
    tags = TagField(blank=True)

    objects = NewsManager()
    class Meta:
        permissions = (("view_news","Can view news"),)
        verbose_name_plural = "news"

    @models.permalink
    def get_absolute_url(self):
        return ("news.view", [self.pk])

    def __unicode__(self):
        return self.headline