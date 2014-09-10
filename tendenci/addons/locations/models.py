import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from tendenci.core.base.fields import SlugField
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.addons.locations.managers import LocationManager
from tendenci.addons.locations.utils import get_coordinates
from tendenci.core.files.models import File


class Location(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    location_name = models.CharField(_('Name'), max_length=200, blank=True)
    slug = SlugField(_('URL Path'), unique=True)
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
    logo = models.ForeignKey(File, null=True, default=None,
                             help_text=_('Only jpg, gif, or png images.'))
    hq = models.BooleanField(_('Headquarters'))

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = LocationManager()

    class Meta:
        permissions = (("view_location",_("Can view location")),)

    def __unicode__(self):
        return self.location_name

    @models.permalink
    def get_absolute_url(self):
        return ("location", [self.slug])

    def get_address(self):
        return "%s %s %s, %s %s" % (
            self.address,
            self.address2,
            self.city,
            self.state,
            self.zipcode
        )

    def distance_api(self, **kwargs):
        import simplejson, urllib
        DISTANCE_BASE_URL = 'http://maps.googleapis.com/maps/api/distancematrix/json?'
        kwargs.update({
            'origins':kwargs.get('origin',''),
            'destinations':self.get_address(),
            'sensor':'false',
            })
        url = '%s?%s' % (DISTANCE_BASE_URL, urllib.urlencode(kwargs))
        return simplejson.load(urllib.urlopen(url))

    def get_distance(self, **kwargs):
        """
        Pings the Google Map API (DistanceMatrix).
        Returns the distance in miles.
        """
        origin = kwargs.get('origin')
        result = distance_api(**{'origin':origin})

        if result['status'] == 'OK':
            # return result['rows'][0]['elements'][0]['duration']['value']
            return result['rows'][0]['elements'][0]['distance']['value']

        return None

    def get_distance2(self, lat, lng):
        """
        http://www.johndcook.com/python_longitude_latitude.html
        Distance in miles multiply by 3960
        Distance in kilometers multiply by 6373
        """
        import math
        from time import clock, time

        # if we don't have latitude or longitude
        # we return a none type object instead of int
        if not all((self.latitude, self.longitude)):
            return None

        # Convert latitude and longitude to
        # spherical coordinates in radians.
        degrees_to_radians = math.pi/180.0

        # phi = 90 - latitude
        phi1 = (90.0 - self.latitude)*degrees_to_radians
        phi2 = (90.0 - lat)*degrees_to_radians

        # theta = longitude
        theta1 = self.longitude*degrees_to_radians
        theta2 = lng*degrees_to_radians

        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
               math.cos(phi1)*math.cos(phi2))
        try:
            arc = math.acos(cos)
        except:
            arc = 0

        # Remember to multiply arc by the radius of the earth
        # in your favorite set of units to get length.
        return arc * 3960

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())

        # update latitude and longitude
        if not all((self.latitude, self.longitude)):
            self.latitude, self.longitude = get_coordinates(self.get_address())

        photo_upload = kwargs.pop('photo', None)
        super(Location, self).save(*args, **kwargs)

        if photo_upload and self.pk:
            image = File(content_type=ContentType.objects.get_for_model(self.__class__),
                         object_id=self.pk,
                         creator=self.creator,
                         creator_username=self.creator_username,
                         owner=self.owner,
                         owner_username=self.owner_username)
            photo_upload.file.seek(0)
            image.file.save(photo_upload.name, photo_upload)
            image.save()

            self.logo = image
            self.save()


class LocationImport(models.Model):

    creator = models.ForeignKey(User)
    create_dt = models.DateTimeField(auto_now_add=True)

    def get_file(self):
        file = File.objects.get_for_model(self)[0]
        return file

    def __unicode__(self):
        return self.get_file().file.path


class Distance(models.Model):
    """Holds distance information between zip codes and locations"""
    zip_code = models.CharField(max_length=7)
    location = models.ForeignKey(Location)
    distance = models.PositiveSmallIntegerField()

    def get_locations(zip_code):
        return Distance.objects.filter(zip_code=zip_code).order_by('distance')
