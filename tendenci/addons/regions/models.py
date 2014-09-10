import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.addons.regions.managers import RegionManager


class Region(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    region_name = models.CharField(_('Name'), max_length=200)
    region_code = models.CharField(_('Region Code'), max_length=200)
    description = models.TextField(blank=True, default='')

    perms = generic.GenericRelation(ObjectPermission,
                                  object_id_field="object_id",
                                  content_type_field="content_type")

    objects = RegionManager()

    class Meta:
        permissions = (("view_region", _("Can view region")),)
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    def __unicode__(self):
        return self.region_name

#    @models.permalink
#    def get_absolute_url(self):
#        return ("industry", [self.pk])

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())

        super(Region, self).save(*args, **kwargs)
