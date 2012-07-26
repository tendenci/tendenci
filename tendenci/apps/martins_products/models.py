from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from tendenci.core.files.models import File
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.apps.martins_products.managers import ProductManager

class Category(models.Model):
    name = models.CharField(_(u'Name'), max_length=200,)
    
    def __unicode__(self):
        return unicode(self.name)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    @models.permalink
    def get_absolute_url(self):
        return ("product.category", [self.pk])


class Formulation(models.Model):
    name = models.CharField(_(u'Name'), max_length=200,)
    
    def __unicode__(self):
        return unicode(self.name)


class Product(TendenciBaseModel):
    """
    Products plugin comments
    """
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    category_num = models.CharField(_(u'Category Id'), max_length=200, blank=True,) # To avoid conflicting column names
    category = models.ForeignKey('Category', null=True, blank=True,)
    product_id = models.CharField(_(u'Product Id'), max_length=200, blank=True,)
    product_name = models.CharField(_(u'Product Name'), max_length=200,)
    product_slug = models.SlugField(max_length=200, unique=True,)
    generic_description = models.TextField(_(u'Generic Description'), blank=True,)
    brand = models.CharField(_(u'Brand'), max_length=200, blank=True,)
    product_features = models.TextField(_(u'Product Features'), blank=True,)
    product_code = models.CharField(_(u'Product Code'), max_length=200, blank=True,)
    product_specs = models.TextField(_(u'Product Specs'), blank=True,)
    formulation = models.ForeignKey(Formulation)
    active_ingredients = models.CharField(_(u'Active Ingredients'), max_length=200, blank=True,)
    key_insects = models.CharField(_(u'Key Insects'), max_length=200, blank=True,)
    use_sites = models.CharField(_(u'Use Sites'), max_length=200, blank=True,)
    msds_label = models.CharField(_(u'MSDS Label'), max_length=200, blank=True,)
    product_label = models.CharField(_(u'Product Label'), max_length=200, blank=True,)
    state_registered = models.CharField(_(u'State Registered'), max_length=200, blank=True,)
    product_image = models.ForeignKey('ProductPhoto',
        help_text=_('Photo that represents this product.'), null=True, default=None, blank=True,)
    hover_image = models.ForeignKey('HoverPhoto',
        help_text=_('Photo that will show when the product is hovered over in search.'), null=True, default=None, blank=True,)
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = ProductManager()
    
    def __unicode__(self):
        return self.product_name
    
    class Meta:
        permissions = (("view_product","Can view product"),)
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def photo(self):
        if self.product_image and self.product_image.file:
            return self.product_image.file

        return None

    @models.permalink
    def get_absolute_url(self):
        return ("products.detail", [self.product_slug])


class ProductPhoto(File):
    @property
    def content_type(self):
        return 'products'
        
class HoverPhoto(File):
    @property
    def content_type(self):
        return 'products'