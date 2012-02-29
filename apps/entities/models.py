import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from perms.models import TendenciBaseModel
from perms.object_perms import ObjectPermission
from entities.managers import EntityManager

class Entity(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    entity_name = models.CharField(_('Name'), max_length=200, blank=True)
    entity_type = models.CharField(_('Type'), max_length=200, blank=True)
    entity_parent_id = models.IntegerField(_('Parent ID'), default=0)
      
    # contact info
    contact_name = models.CharField(_('Contact Name'), max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)
    summary = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = EntityManager()

    class Meta:
        permissions = (("view_entity","Can view entity"),)
        verbose_name_plural = "entities"
        
    def __unicode__(self):
        return self.entity_name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            
        super(Entity, self).save(*args, **kwargs)


