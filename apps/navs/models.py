from django.db import models
from django.utils.translation import ugettext_lazy as _

from perms.models import TendenciBaseModel
from navs.managers import NavManager

class Nav(TendenciBaseModel):
    class Meta:
        permissions = (("view_nav","Can view nav"),)
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    megamenu = models.BooleanField(default=False)
    
    objects = NavManager()
    
    def __unicode__(self):
        return self.title
        
    @models.permalink
    def get_absolute_url(self):
        return('navs.detail', [self.pk])
    
class NavItem(models.Model):
    menu = models.ForeignKey(Nav)
    label = models.CharField(max_length=100)
    link = models.URLField()
    
    def __unicode__(self):
        return '%s - %s' % (self.menu.title, self.label)
