from django.db import models
from django.utils.translation import ugettext_lazy as _

from perms.models import TendenciBaseModel
from pages.models import Page
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
    
    @property
    def items(self, level=0):
        # get all items of a given level
        rel = self.navitem_set.filter(level=level)
        return rel
    
class NavItem(models.Model):
    nav = models.ForeignKey(Nav)
    label = models.CharField(max_length=100)
    title = models.CharField(_("Title Attribute"), max_length=100, blank=True, null=True)
    css = models.CharField(_("CSS Class"), max_length=100, blank=True, null=True)
    ordering = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    page = models.ForeignKey(Page)
    
    def __unicode__(self):
        return '%s - %s' % (self.nav.title, self.label)
    
    @property
    def children(self):
        # gets all subnavigations
        rel = self.nav.navitem_set.filter(ordering=self.ordering)
        children = rel.filter(level=self.level+1)
        return children
        
