from django.db import models
from base.fields import SlugField
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from files.models import File
from tenents.managers import TenentManager, MapManager


class Map(File):
    """
    This is an image of the map that tenents will
    be defined on. Clicking on hotspots of a map give you
    details about the tenent you clicked.
    """
    objects = MapManager()

    class Meta:
        permissions = (("view_map", "Can view map"),)

    def __unicode__(self):
        return self.get_name()

    slug = SlugField(_('URL Path'), unique=True)

    @property
    def content_type(self):
        return 'tenents'

    def height_for(self, new_width):
        iwidth, iheight = self.image_dimensions()
        new_height = iheight * new_width / iwidth
        return new_height


class Kind(models.Model):
    """
    Kind of tenent. Used for organizing and filtering.
    """
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=10, null=True, blank=True)

    def __unicode__(self):
        return self.name


class Tenent(TendenciBaseModel):
    """
    A Tenent is a set of coordinates.
    Coordinates are integer 2-tuples that describe a point on an uploaded image.
    The uploaded image can also be identified as the map.
    """
    map = models.ForeignKey(Map)
    kind = models.ForeignKey(Kind)
    name = models.CharField(_(u'Name'), max_length=200)
    slug = SlugField(_('URL Path'), unique=True)

    phone = models.CharField(max_length=20, blank=True)
    link = models.URLField(blank=True)

    description = models.TextField(_(u'Description'), blank=True)
    suite_number = models.CharField(max_length=10, blank=True)

    hours_open = models.TextField(_(u'Hours of Operation'), blank=True)
    contact_info = models.TextField(_(u'Contact Information'), blank=True)

    tags = TagField(blank=True, help_text=u'e.g. restaurant, ctenenthing, restroom')

    objects = TenentManager()

    class Meta:
        permissions = (("view_tenent", "Can view tenent"),)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("tenents.detail", [self.pk])


class Photo(File):
    """
    This is the photo associated
    with a tenent. A tenent can have one photo.
    The photo can be deleted without affecting
    the tenent.  If the tenent is deleted, the
    photo is also deleted.
    """
    tenent = models.OneToOneField(Tenent)

    @property
    def content_type(self):
        return 'tenents'


class Line(models.Model):
    """
    Line coordinates for a tenent.
    """
    tenent = models.ForeignKey(Tenent)
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
