from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from tagging.fields import TagField
from meta.models import Meta as MetaTags
from perms.models import TendenciBaseModel
from files.models import file_directory

from before_and_after.module_meta import BeforeAndAfterMeta

class Category(models.Model):
    name = models.CharField(_('name'), max_length=200)
    image = models.ImageField(upload_to=file_directory, null=True, blank=True)
    
    class Meta:
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name
    
class Subcategory(models.Model):
    name = models.CharField(_('name'), max_length=200)
    warning = models.BooleanField(_('display warning'))
    
    class Meta:
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name
        

class BeforeAndAfter(models.Model):
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True)
    category = models.ForeignKey(Category)
    description = models.TextField(_('description'))
    subcategory = models.ForeignKey(Subcategory, null=True, blank=True)
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))
    admin_notes = models.TextField(_('admin notes'), blank=True)
    meta = models.OneToOneField(MetaTags, null=True, blank=True)
    
    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        methods coupled to this instance.
        """
        return BeforeAndAfterMeta().get_meta(self, name)
    
    @models.permalink
    def get_absolute_url(self):
        return ('before_and_after.detail', [self.slug])

    def __unicode__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(BeforeAndAfter, self).save(*args, **kwargs)
        

class PhotoSet(models.Model):
    
    before_and_after = models.ForeignKey(BeforeAndAfter)
    before_photo = models.ImageField(upload_to=file_directory)
    after_photo = models.ImageField(upload_to=file_directory)
    description = models.TextField(_('description'), blank=True)
    
    @property
    def content_type(self):
        return 'before_and_after'
    
    def __unicode__(self):
        return self.before_and_after.title
