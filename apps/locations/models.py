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

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    hq = models.BooleanField(_('Headquarters'))
    entity = models.ForeignKey(Entity,null=True, blank=True)

    objects = LocationManager()

    class Meta:
        permissions = (("view_location","Can view location"),)

    def __unicode__(self):
        return self.description

    @models.permalink
    def get_absolute_url(self):
        return ("location", [self.pk])

    def get_address(self):
        return "%s %s %s, %s %s" % (
            self.address, 
            self.address2, 
            self.city, 
            self.state, 
            self.zipcode
        )

    def get_coordinates(self):
        import simplejson, urllib
        GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
        kwargs.update({'address':self.get_address(),'sensor':'false'})
        url = '%s?%s' % (GEOCODE_BASE_URL, urllib.urlencode(kwargs))
        result = simplejson.load(urllib.urlopen(url))

        if result['status'] == 'OK':
            return result['results'][0]['geometry']['location'].values()
        
        return (None, None)

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())

        # update latitude and longitude
        if not all((self.latitude, self.longitude)):
            self.latitude, self.longitude = self.get_coordinates()

        super(Location, self).save(*args, **kwargs)

class Distance(models.Model):
    """Holds distance information between zip codes and locations"""
    zip_code = models.CharField(max_length=7)
    location = models.ForeignKey(Location)
    distance = models.PositiveSmallIntegerField()

    def get_locations(zip_code):
        return Distance.objects.filter(zip_code=zip_code).order_by('distance')