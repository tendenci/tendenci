from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from S_P_LOW.managers import S_S_CAPManager

class S_S_CAP(TendenciBaseModel):
    """
    S_P_CAP plugin comments
    """
    title = models.CharField(_('title'), max_length=100, blank=True)
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    
    objects = S_S_CAPManager()
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        permissions = (("view_S_S_LOW","Can view S_S_LOW"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("S_S_LOW.detail", [self.pk])