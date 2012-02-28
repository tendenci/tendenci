from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from stories.models import Story
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
    website = models.CharField(_(u'Website'), max_length=200)
    building_photo = models.ImageField(_(u'Building Photo'), upload_to=file_directory)
    about = models.TextField(_(u'About'))
    
    ## Visitor Information
    hours = models.TextField(_(u'Hours'))
    free_times = models.TextField(_(u'Free Times'))
    parking_information = models.TextField(_(u'Parking Information'))
    free_parking = models.BooleanField(_(u'Free Parking?'), default=False)
    street_parking = models.BooleanField(_(u'Street Parking?'), default=False)
    paid_parking = models.BooleanField(_(u'Paid Parking?'), default=False)
    dining_information = models.TextField(_(u'Dining Information'), blank=True)
    restaurant = models.BooleanField(_(u'Restaurant?'), default=False)
    snacks = models.BooleanField(_(u'Snacks?'), default=False)
    shopping_information = models.TextField(_(u'Shopping Information'), blank=True)
    events = models.CharField(_(u'Events'), max_length=200, blank=True)
    special_offers = models.ManyToManyField(Story, default=None, blank=True)
    
    ## Stay Connected
    facebook = models.CharField(_(u'Facebook'), max_length=200, blank=True)
    twitter = models.CharField(_(u'Twitter'), max_length=200, blank=True)
    flickr = models.CharField(_(u'Flickr'), max_length=200, blank=True)
    youtube = models.CharField(_(u'YouTube'), max_length=200, blank=True)
    
    slug = models.SlugField(max_length=200, unique=True, default="")
    ordering = models.IntegerField(blank=True, null=True)
    
    objects = MuseumManager()
    
    def __unicode__(self):
        return unicode(self.name)
    
    def save(self, *args, **kwargs):
        model = self.__class__

        if self.ordering is None:
            # Append
            try:
                last = model.objects.order_by('-ordering')[0]
                self.ordering = last.ordering + 1
            except IndexError:
                # First row
                self.ordering = 0

        return super(Museum, self).save(*args, **kwargs)
    
    class Meta:
        permissions = (("view_museum","Can view museum"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("museums.detail", [self.slug])
        
    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)
        
    @property
    def full_address(self):
        return "%s, %s, %s" % (self.address, self.city, self.state)

    def get_special_offers(self):
        from datetime import datetime
        from django.db.models import Q
        now = datetime.now()

        # Considering special offers that expire
        return self.special_offers.filter(
            Q(expires=True, start_dt__lte=now, end_dt__gte=now) | Q(expires=False, start_dt__lte=now)
        )

class Photo(File):
    museum = models.ForeignKey(Museum, related_name="photos")
