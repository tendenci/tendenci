from django.db import models
from base.fields import SlugField
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from files.models import File
from tenants.managers import TenantManager, MapManager


class Map(File):
    """
    This is an image of the map that tenants will
    be defined on. Clicking on hotspots of a map give you
    details about the tenant you clicked.
    """
    objects = MapManager()

    class Meta:
        permissions = (("view_map", "Can view map"),)

    def __unicode__(self):
        return self.get_name()

    slug = SlugField(_('URL Path'), unique=True)

    @property
    def content_type(self):
        return 'tenants'

    def height_for(self, new_width):
        iwidth, iheight = self.image_dimensions()
        new_height = iheight * new_width / iwidth
        return new_height


class Kind(models.Model):
    """
    Kind of tenant. Used for organizing and filtering.
    """
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=10, null=True, blank=True)

    def __unicode__(self):
        return self.name


class Tenant(TendenciBaseModel):
    """
    A Tenant is a set of coordinates.
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

    tags = TagField(blank=True, help_text=u'e.g. restaurant, ctenanthing, restroom')

    objects = TenantManager()

    class Meta:
        permissions = (("view_tenant", "Can view tenant"),)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("tenants.detail", [self.pk])


class Photo(File):
    """
    This is the photo associated
    with a tenant. A tenant can have one photo.
    The photo can be deleted without affecting
    the tenant.  If the tenant is deleted, the
    photo is also deleted.
    """
    tenant = models.OneToOneField(Tenant)

    @property
    def content_type(self):
        return 'tenants'


class Line(models.Model):
    """
    Line coordinates for a tenant.
    """
    tenant = models.ForeignKey(Tenant)
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
