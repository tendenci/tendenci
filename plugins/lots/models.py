from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from files.models import File
from lots.managers import LotManager, MapManager


class Map(File):
    """
    This is an image of the map that lots will
    be defined on. Clicking on hotspots of a map give you
    details about the lot you clicked.
    """
    objects = MapManager()

    class Meta:
        permissions = (("view_map", "Can view map"),)

    def __unicode__(self):
        return self.get_name()

    @property
    def content_type(self):
        return 'lots'

    def height_for(self, new_width):
        iwidth, iheight = self.image_dimensions()
        new_height = iheight * new_width / iwidth
        return new_height


class Lot(TendenciBaseModel):
    """
    A Lot is a set of coordinates.
    Coordinates are integer 2-tuples that describe a point on an uploaded image.
    The uploaded image can also be identified as the map.
    """
    map = models.ForeignKey(Map)
    name = models.CharField(_(u'Name'), max_length=200)

    phone = models.CharField(max_length=20, blank=True)
    link = models.URLField(blank=True)

    description = models.TextField(_(u'Description'), blank=True)
    suite_number = models.CharField(max_length=10, blank=True)

    hours_open = models.TextField(_(u'Hours of Operation'), blank=True)
    contact_info = models.TextField(_(u'Contact Information'), blank=True)

    tags = TagField(blank=True, help_text=u'e.g. restaurant, clothing, restroom')

    objects = LotManager()

    class Meta:
        permissions = (("view_lot", "Can view lot"),)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("lots.detail", [self.pk])


class Photo(File):
    """
    This is the photo associated
    with a lot. A lot can have multiple photos.
    """
    lot = models.OneToOneField(Lot)

    @property
    def content_type(self):
        return 'lots'


class Line(models.Model):
    """
    Line coordinates for a lot.
    """
    lot = models.ForeignKey('Lot')
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
