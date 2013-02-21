import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.addons.industries.managers import IndustryManager


class Industry(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    industry_name = models.CharField(_('Name'), max_length=200)
    industry_code = models.CharField(_('Industry Code'), max_length=200)
    description = models.TextField(blank=True, default='')

    perms = generic.GenericRelation(ObjectPermission,
                                  object_id_field="object_id",
                                  content_type_field="content_type")

    objects = IndustryManager()

    class Meta:
        permissions = (("view_industry", "Can view industry"),)
        verbose_name = "Industry"
        verbose_name_plural = "Industries"

    def __unicode__(self):
        return self.industry_name

#    @models.permalink
#    def get_absolute_url(self):
#        return ("industry", [self.pk])

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())

        super(Industry, self).save(*args, **kwargs)
