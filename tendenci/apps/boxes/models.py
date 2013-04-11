from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.contenttypes import generic

from tendenci.core.perms.object_perms import ObjectPermission
from tagging.fields import TagField
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.boxes.managers import BoxManager
from tinymce import models as tinymce_models

class Box(OrderingBaseModel, TendenciBaseModel):
    title = models.CharField(max_length=500, blank=True)
    content = tinymce_models.HTMLField()
    tags = TagField(blank=True)

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = BoxManager()

    class Meta:
        permissions = (("view_box","Can view box"),)
        verbose_name_plural = "Boxes"
        ordering = ['position']
    
    def __unicode__(self):
        return self.title
        
    def safe_content(self):
        return mark_safe(self.content)

    def save(self, *args, **kwargs):
        model = self.__class__
        
        if self.position is None:
            # Append
            try:
                last = model.objects.order_by('-position')[0]
                self.ordering = last.ordering + 1
            except IndexError:
                # First row
                self.ordering = 0

        return super(Box, self).save(*args, **kwargs)
