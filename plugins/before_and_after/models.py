from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings

from tagging.fields import TagField
from meta.models import Meta as MetaTags
from perms.models import TendenciBaseModel
from files.models import file_directory

from before_and_after.module_meta import BeforeAndAfterMeta
from before_and_after.managers import BeforeAndAfterManager

class Category(models.Model):
    name = models.CharField(_('name'), max_length=200, unique=True)
    image = models.ImageField(upload_to=file_directory, null=True, blank=True)
    
    @property
    def default_image(self):
        return settings.STATIC_URL + "/images/default-photo.jpg"
    
    @property
    def content_type(self):
        return 'before_and_after'
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name
    
class Subcategory(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(_('name'), max_length=200)
    warning = models.BooleanField(_('display warning'))
    
    class Meta:
        verbose_name_plural = "Subcategories"
        unique_together = ("category", "name")
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name
        

class BeforeAndAfter(TendenciBaseModel):
    title = models.CharField(_('title'), max_length=200)
    category = models.ForeignKey(Category)
    description = models.TextField(_('description'))
    subcategory = models.ForeignKey(Subcategory, null=True, blank=True)
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))
    admin_notes = models.TextField(_('admin notes'), blank=True)
    meta = models.OneToOneField(MetaTags, null=True, blank=True)
    
    objects = BeforeAndAfterManager()
    
    class Meta:
        verbose_name = _('Before & After')
        verbose_name_plural = _('Before & Afters')
        permissions = (("view_before_and_after","Can view Before and After"),)
    
    @property
    def featured(self):
        """
        Returns the featured before and after photoset.
        The first photoset in the list.
        """
        photosets = self.photoset_set.all().order_by('order')
        try:
            return photosets[0]
        except:
            return None
    
    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        methods coupled to this instance.
        """
        return BeforeAndAfterMeta().get_meta(self, name)
    
    @models.permalink
    def get_absolute_url(self):
        return ('before_and_after.detail', [self.id])

    def __unicode__(self):
        return self.title
        

class PhotoSet(models.Model):
    order = models.IntegerField(_('order'), blank=True, null=True)
    before_and_after = models.ForeignKey(BeforeAndAfter)
    before_photo = models.ImageField(upload_to=file_directory)
    after_photo = models.ImageField(upload_to=file_directory)
    description = models.TextField(_('description'), blank=True)
    
    @property
    def content_type(self):
        return 'before_and_after'
    
    def __unicode__(self):
        return self.before_and_after.title
