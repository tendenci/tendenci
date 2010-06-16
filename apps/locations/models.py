from django.db import models
from tagging.fields import TagField
from timezones.fields import TimeZoneField
from perms.models import AuditingBaseModel
from locations.managers import LocationManager

class Location(AuditingBaseModel):

    # TODO: make unique=True (dependent on migration script)
    guid = models.CharField(max_length=50, unique=False, blank=True)
 
    location_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    # contact/location information 
    contact = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=50, blank=True)   
    country = models.CharField(max_length=100, blank=True)      
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)
    
    # TODO - figure out if these stay
    latitude = models.FloatField()
    longitude = models.FloatField()

    hq = models.BooleanField()
    
    entityid = models.IntegerField()
    entityownerid = models.IntegerField()

    create_dt = models.DateTimeField(auto_now_add=True)
        
    objects = LocationManager()

    class Meta:
        permissions = (("view_location","Can view location"),)

    @models.permalink
    def get_absolute_url(self):
        return ("location", [self.pk])

    def __unicode__(self):
        return self.description
