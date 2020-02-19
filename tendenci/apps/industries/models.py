from builtins import str
import uuid

from django.db import models
#from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.industries.managers import IndustryManager
from tendenci.libs.abstracts.models import OrderingBaseModel


class Industry(OrderingBaseModel, TendenciBaseModel):
    guid = models.CharField(max_length=40)
    industry_name = models.CharField(_('Name'), max_length=200)
    industry_code = models.CharField(_('Industry Code'), max_length=200)
    description = models.TextField(blank=True, default='')

    perms = GenericRelation(ObjectPermission,
                                  object_id_field="object_id",
                                  content_type_field="content_type")

    objects = IndustryManager()

    class Meta:
#         permissions = (("view_industry", _("Can view industry")),)
        verbose_name = _("Industry")
        verbose_name_plural = _("Industries")
        ordering = ('position','-update_dt')
        app_label = 'industries'

    def __str__(self):
        return self.industry_name

#    def get_absolute_url(self):
#        return reverse('industry', args=[self.pk])

    def save(self, *args, **kwargs):
        self.guid = self.guid or str(uuid.uuid4())

        super(Industry, self).save(*args, **kwargs)
