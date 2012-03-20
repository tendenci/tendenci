from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from base.fields import SlugField
from perms.models import TendenciBaseModel
from perms.object_perms import ObjectPermission
from products.managers import ProductManager, ProductFileManager
from files.models import File


class Category(models.Model):
    name = models.CharField(_('name'), max_length=200, unique=True)

    @property
    def content_type(self):
        return 'product'

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(_('name'), max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "Subcategories"
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Product(TendenciBaseModel):
    """
    Products plugin lists out different products
    """
    name = models.CharField(_(u'name'), help_text=u'', blank=False, max_length=200, default=u'',)
    slug = models.SlugField(_(u'slug'), unique=True, blank=False, max_length=200, default=u'',)
    brand = models.CharField(_(u'brand'), help_text=u'', blank=True, max_length=200, default=u'',)
    url = models.URLField(_(u'url'), help_text=u'URL outside of this site for the product.', blank=True, max_length=200, default=u'',)
    item_number = models.CharField(_(u'item number'), help_text=u'', blank=True, max_length=200, default=u'',)
    category = models.ForeignKey(Category, null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, null=True, blank=True)
    summary = models.TextField(_(u'summary'), help_text=u'A brief summary that can be shown in search results.', blank=True, default=u'',)
    description = models.TextField(_(u'description'), help_text=u'', blank=False, default=u'')
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')

    perms = generic.GenericRelation(ObjectPermission, 
        object_id_field="object_id", content_type_field="content_type")

    objects = ProductManager()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        permissions = (("view_product","Can view product"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("products.detail", [self.slug])


class ProductFile(File):
    product = models.ForeignKey(Product)
    photo_description = models.CharField(_('description'), max_length=50, blank=True)
    position = models.IntegerField(blank=True)

    objects = ProductFileManager()

    def save(self, *args, **kwargs):
        if self.position is None:
            # Append
            try:
                last = ProductFile.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(ProductFile, self).save(*args, **kwargs)

    class Meta:
        ordering = ('position',)