from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from plugs.managers import PlugManager

class Plug(TendenciBaseModel):
    """
    Plugs plugin comments
    """
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    name = models.CharField(_(u'name'), help_text=u'Name it Bro', blank=False, max_length=200, default=u'',)
    number = models.IntegerField(_(u'number'), help_text=u'WathWa?', blank=False, default=1,)
    brother = models.TextField(_(u'brother'), help_text=u'', blank=True, default=u'',)
    multiline_one = models.TextField(_(u'multiline_one'), help_text=u'', blank=True, default=u'',)
    start = models.DateTimeField(_(u'start'), help_text=u'', blank=True, default=u'',)
    objects = PlugManager()
    
    def __unicode__(self):
        return self.id
    
    class Meta:
        permissions = (("view_plug","Can view plug"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("plug.detail", [self.pk])
