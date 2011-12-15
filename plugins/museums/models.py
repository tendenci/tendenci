from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from files.models import file_directory, File

from museums.managers import MuseumManager

class Museum(TendenciBaseModel):
    """
    Museums plugin comments
    """
    
    ## Basic Information
    name = models.CharField(_(u'Name'), max_length=200)
    phone = models.CharField(_(u'Phone'), max_length=200)
    address = models.TextField(_(u'Address'))
    city = models.CharField(_(u'City'), max_length=200)
    state = models.CharField(_(u'State'), max_length=200)
    zip = models.CharField(_(u'Zip'), max_length=200)
    website = models.URLField(_(u'Website'), max_length=200)
    building_photo = models.ImageField(_(u'Building Photo'), upload_to=file_directory)
    about = models.TextField(_(u'About'),)
    
    ## Visitor Information
    hours = models.TextField(_(u'Hours'),)
    free_times = models.TextField(_(u'Free Times'),)
    parking_information = models.TextField(_(u'Parking Information'),)
    free_parking = models.BooleanField(_(u'Free Parking?'), default=False)
    street_parking = models.BooleanField(_(u'Street Parking?'), default=False)
    paid_parking = models.BooleanField(_(u'Paid Parking?'), default=False)
    dining_information = models.TextField(_(u'Dining Information'))
    restaurant = models.BooleanField(_(u'Restaurant?'), default=False)
    snacks = models.BooleanField(_(u'Snacks?'), default=False)
    shopping_information = models.TextField(_(u'Shopping Information'))
    events = models.CharField(_(u'Events'), max_length=200)
    special_offers = models.TextField(_(u'Special Offers'))
    
    ## Stay Connected
    facebook = models.URLField(_(u'Facebook'), max_length=200)
    twitter = models.CharField(_(u'Twitter'), max_length=200)
    flickr = models.CharField(_(u'Flickr'), max_length=200)
    youtube = models.URLField(_(u'YouTube'), max_length=200)
    
    objects = MuseumManager()
    
    def __unicode__(self):
        return unicode(self.name)
    
    class Meta:
        permissions = (("view_museum","Can view museum"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("museum.detail", [self.pk])

class Photo(File):
    museum = models.ForeignKey(Museum)
