from django.db import models
from django.utils.translation import ugettext_lazy as _

from perms.models import TendenciBaseModel

class Nav(TendenciBaseModel):
    class Meta:
        permissions = (("view_discount","Can view discount"),)
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    megamenu = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.title
    
class NavItem(models.Model):
    menu = models.ForeignKey(Nav)
    label = models.CharField(max_length=100)
    link = models.URLField()
    
    def __unicode__(self):
        return '%s - %s' % (self.menu.title, self.label)
