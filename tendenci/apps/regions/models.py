from builtins import str
import uuid

from django.db import models
#from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.regions.managers import RegionManager
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.site_settings.utils import get_setting


class Region(OrderingBaseModel, TendenciBaseModel):
    guid = models.CharField(max_length=40)
    region_name = models.CharField(_('Name'), max_length=200)
    region_code = models.CharField(_('Region Code'), max_length=200)
    description = models.TextField(blank=True, default='')

    tax_rate = models.DecimalField(blank=True, max_digits=6, decimal_places=5, default=0,
                                   help_text=_('Example: 0.0825 for 8.25%.'))
    tax_label_2 = models.CharField(_('Label for tax 2'), max_length=6, blank=True, default='')
    tax_rate_2 = models.DecimalField(blank=True, max_digits=6, decimal_places=5, default=0,
                                   help_text=_('Example: 0.0825 for 8.25%.'))
    invoice_header = models.TextField(blank=True, default='')
    invoice_footer = models.TextField(blank=True, default='')

    perms = GenericRelation(ObjectPermission,
                                  object_id_field="object_id",
                                  content_type_field="content_type")

    objects = RegionManager()

    class Meta:
#         permissions = (("view_region", _("Can view region")),)
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")
        ordering = ['position']
        app_label = 'regions'

    def __str__(self):
        return self.region_name

#    def get_absolute_url(self):
#        return reverse('industry', args=[self.pk])

    @classmethod
    def get_region_by_name(cls, region_name):
        return cls.objects.filter(region_name=region_name).order_by('status_detail').first()

    def save(self, *args, **kwargs):
        self.guid = self.guid or str(uuid.uuid4())

        super(Region, self).save(*args, **kwargs)

    def invoice_header_with_absurl(self):
        """
        Replace relative to absolute urls for invoice_header
        """
        site_url = get_setting('site', 'global', 'siteurl')
        temp_header = self.invoice_header.replace("src=\"/", f"src=\"{site_url}/")
        temp_header = temp_header.replace("href=\"/", f"href=\"{site_url}/")
        return temp_header

    def invoice_footer_with_absurl(self):
        """
        Replace relative to absolute urls for invoice_header
        """
        site_url = get_setting('site', 'global', 'siteurl')
        temp_footer = self.invoice_footer.replace("src=\"/", f"src=\"{site_url}/")
        temp_footer = temp_footer.replace("href=\"/", f"href=\"{site_url}/")
        return temp_footer
