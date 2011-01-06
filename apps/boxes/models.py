from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from boxes.managers import BoxManager
from tinymce import models as tinymce_models

class Box(TendenciBaseModel):
    title = models.CharField(max_length=500, blank=True)
    content = tinymce_models.HTMLField()
    tags = TagField(blank=True)
    
    objects = BoxManager()

    class Meta:
        permissions = (("view_box","Can view box"),)
        verbose_name_plural = "Boxes"
    
    def __unicode__(self):
        return self.title
        
    def safe_content(self):
        return mark_safe(self.content)