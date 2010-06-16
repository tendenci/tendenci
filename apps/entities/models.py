from django.db import models

from perms.models import AuditingBaseModel

class Entity(AuditingBaseModel):

    # TODO: make unique=True (dependent on migration script)
    guid = models.CharField(max_length=50, unique=False, blank=True)
    entity_name = models.CharField(max_length=200, blank=True)
    entitytype = models.CharField(max_length=200, blank=True)
    entityownerid = models.IntegerField(default=0)
    entityparentid = models.IntegerField(default=0)
      
    # contact info
    contact_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)

    summary = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)


    class Meta:
        permissions = (("view_entity","Can view entity"),)
        
    def __unicode__(self):
        return self.entity_name


