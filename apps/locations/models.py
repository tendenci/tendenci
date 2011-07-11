import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _

from perms.models import TendenciBaseModel 
from locations.managers import LocationManager
from entities.models import Entity

class Location(TendenciBaseModel):
    guid = models.CharField(max_length=40) 
    location_name = models.CharField(_('Name'), max_length=200, blank=True)
    description = models.TextField(blank=True)

    # contact/location information 
    contact = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(_('Zip Code'), max_length=50, blank=True)   
    country = models.CharField(max_length=100, blank=True)      
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)
    
    # TODO - figure out if these stay
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    hq = models.BooleanField(_('Headquarters'))
    
    entity = models.ForeignKey(Entity,null=True, blank=True)
        
    objects = LocationManager()

    class Meta:
        permissions = (("view_location","Can view location"),)

    @models.permalink
    def get_absolute_url(self):
        return ("location", [self.pk])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            
        super(Location, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.description
