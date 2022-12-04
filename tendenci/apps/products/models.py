from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse

from tagging.fields import TagField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from .managers import ProductManager, ProductFileManager
from tendenci.apps.files.models import File


class Category(models.Model):
    name = models.CharField(_('name'), max_length=200, unique=True)

    @property
    def content_type(self):
        return 'product'

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(TendenciBaseModel):
    name = models.CharField(blank=False, max_length=200, default='',)
    slug = models.SlugField(unique=True, blank=False, max_length=200,)
    brand = models.CharField(blank=True, max_length=200, default='',)
    url = models.URLField(help_text=_('URL outside of this site for the product.'), 
                          blank=True, max_length=200, default='',)
    item_number = models.CharField(blank=True, max_length=200, default='',)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL,)
    summary = models.TextField(help_text=_('A brief summary that can be shown in search results.'),
                               blank=True, default='',)
    description = models.TextField(blank=False, default='')
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    perms = GenericRelation(ObjectPermission,
                            object_id_field="object_id",
                            content_type_field="content_type")

    objects = ProductManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        app_label = 'products'

    # def get_absolute_url(self):
    #     return reverse('products.detail', args=[self.slug])


class ProductFile(File):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)
    photo_description = models.CharField(_('Description'), max_length=50, blank=True)
    position = models.IntegerField(blank=True)
    objects = ProductFileManager()

    class Meta:
        ordering = ('position',)

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
