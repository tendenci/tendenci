from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from files.models import File
from perms.models import TendenciBaseModel
from perms.object_perms import ObjectPermission
from categories.models import CategoryItem
from martins_products.managers import ProductManager

class Category(models.Model):
    name = models.CharField(_(u'Name'), max_length=200,)
    
    def __unicode__(self):
        return unicode(self.name)


class Formulation(models.Model):
    name = models.CharField(_(u'Name'), max_length=200,)
    
    def __unicode__(self):
        return unicode(self.name)


class Product(TendenciBaseModel):
    """
    Products plugin comments
    """
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    category_num = models.CharField(_(u'Category Id'), max_length=200,) # To avoid conflicting column names
    #category = models.ForeignKey(Category)
    product_id = models.CharField(_(u'Product Id'), max_length=200,)
    product_name = models.CharField(_(u'Product Name'), max_length=200,)
    product_slug = models.SlugField(max_length=200, unique=True,)
    generic_description = models.TextField(_(u'Generic Description'),)
    brand = models.CharField(_(u'Brand'), max_length=200,)
    product_features = models.TextField(_(u'Product Features'),)
    product_code = models.CharField(_(u'Product Code'), max_length=200,)
    product_specs = models.TextField(_(u'Product Specs'),)
    formulation = models.ForeignKey(Formulation)
    active_ingredients = models.CharField(_(u'Active Ingredients'), max_length=200,)
    key_insects = models.CharField(_(u'Key Insects'), max_length=200,)
    use_sites = models.CharField(_(u'Use Sites'), max_length=200,)
    msds_label = models.URLField(_(u'MSDS Label'), max_length=200,)
    product_label = models.URLField(_(u'Product Label'), max_length=200,)
    state_registered = models.URLField(_(u'State Registered'), max_length=200,)
    product_image = models.ForeignKey('ProductPhoto',
        help_text=_('Photo that represents this product.'), null=True, default=None)
    categories = generic.GenericRelation(CategoryItem,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
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
    
    @property
    def content_type(self):
        return 'stories'
    
    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category__name', 'parent__name'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items

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
