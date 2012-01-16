from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from lots.managers import LotManager

class Lot(TendenciBaseModel):
    """A Lot is a set of coordinates.
    Coordinates are integer 2-tuples that describe a point on an uploaded image.
    The uploaded image can also be identified as the map.
    """
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    name = models.CharField(_(u'name'), max_length=200,)
    objects = LotManager()
    
    def __unicode__(self):
        return unicode(self.id)
    
    class Meta:
        permissions = (("view_lot","Can view lot"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("lots.detail", [self.pk])

class Coordinate(models.Model):
    """Point coordinate for a lot.
    """
    lot = models.ForeignKey('Lot')
    x = models.IntegerField()
    y = models.IntegerField()
