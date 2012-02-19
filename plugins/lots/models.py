from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from files.models import file_directory, File
from lots.managers import LotManager, MapManager

class Map(File):
    """This is an image where users will place lot coordinates on
    """    
    objects = MapManager()
    
    class Meta:
        permissions = (("view_map","Can view map"),)
        
    def __unicode__(self):
        return self.name
        
    @property
    def content_type(self):
        return 'lots'
    
    def height_for(self, new_width):
        iwidth, iheight = self.image_dimensions()
        new_height = iheight*new_width/iwidth
        return new_height
    
class Lot(TendenciBaseModel):
    """A Lot is a set of coordinates.
    Coordinates are integer 2-tuples that describe a point on an uploaded image.
    The uploaded image can also be identified as the map.
    """
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    map = models.ForeignKey(Map)
    name = models.CharField(_(u'Name'), max_length=200,)
    description = models.TextField(_('Description'), blank=True)
    objects = LotManager()
    
    class Meta:
        permissions = (("view_lot","Can view lot"),)
        
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("lots.detail", [self.pk])

class Line(models.Model):
    """Line coordinates for a lot.
    """
    lot = models.ForeignKey('Lot')
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
