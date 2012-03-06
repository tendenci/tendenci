import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from base.fields import SlugField
from timezones.fields import TimeZoneField
from perms.models import TendenciBaseModel
from news.managers import NewsManager
from tinymce import models as tinymce_models
from meta.models import Meta as MetaTags
from news.module_meta import NewsMeta
from entities.models import Entity
from categories.models import CategoryItem
from perms.object_perms import ObjectPermission

class News(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    timezone = TimeZoneField(_('Time Zone'))
    slug = SlugField(_('URL Path'), unique=True)
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
    syndicate = models.BooleanField(_('Include in RSS feed'), default=True)
    design_notes = models.TextField(_('Design Notes'), blank=True)
    enclosure_url = models.CharField(_('Enclosure URL'), max_length=500, blank=True) # for podcast feeds
    enclosure_type = models.CharField(_('Enclosure Type'),max_length=120, blank=True) # for podcast feeds
    enclosure_length = models.IntegerField(_('Enclosure Length'), default=0) # for podcast feeds
    use_auto_timestamp = models.BooleanField(_('Auto Timestamp'))
    tags = TagField(blank=True) 
    entity = models.ForeignKey(Entity,null=True)
        
    # html-meta tags
    meta = models.OneToOneField(MetaTags, null=True)
    
    categories = generic.GenericRelation(CategoryItem,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = NewsManager()
    class Meta:
        permissions = (("view_news","Can view news"),)
        verbose_name_plural = "news"

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return NewsMeta().get_meta(self, name)

    @models.permalink
    def get_absolute_url(self):
        return ("news.view", [self.slug])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            
        super(News, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.headline