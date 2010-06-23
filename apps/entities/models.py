import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _

from perms.models import AuditingBaseModel

class Entity(AuditingBaseModel):
    guid = models.CharField(max_length=40, default=uuid.uuid1)
    entity_name = models.CharField(_('Name'), max_length=200, blank=True)
    entitytype = models.CharField(_('Type'), max_length=200, blank=True)
    entityownerid = models.IntegerField(_('Owner ID'), default=0)
    entityparentid = models.IntegerField(_('Parent ID'), default=0)
      
    # contact info
    contact_name = models.CharField(_('Contact Name'), max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)

    summary = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)


    class Meta:
        permissions = (("view_entity","Can view entity"),)
        
    def __unicode__(self):
        return self.entity_name


