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
    def top_items(self):
        """
        Returns all items with level 0.
        """
        return self.navitem_set.filter(level=0).order_by('ordering')
    
class NavItem(models.Model):
    nav = models.ForeignKey(Nav)
    label = models.CharField(max_length=100)
    title = models.CharField(_("Title Attribute"), max_length=100, blank=True, null=True)
    css = models.CharField(_("CSS Class"), max_length=100, blank=True, null=True)
    ordering = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    page = models.ForeignKey(Page, null=True)
    url = models.CharField(_("URL"), max_length=200, blank=True, null=True)
    
    def __unicode__(self):
        return '%s - %s' % (self.nav.title, self.label)
        
    def get_url(self):
        if self.page:
            return self.page.get_absolute_url()
        else:
            return self.url
        
    @property
    def children(self):
        """
        returns the item's direct children
        """
        #get the first sibling among the ones with greater ordering
        siblings = NavItem.objects.filter(nav=self.nav,
            ordering__gt=self.ordering,
            level=self.level).order_by('ordering')
        if siblings:
            sibling = siblings[0]
            #return all the items between the adjacent siblings.
            children = NavItem.objects.filter(nav=self.nav,
                level = self.level+1,
                ordering__gt=self.ordering,
                ordering__lt=sibling.ordering).order_by('ordering')
            return children
        else:
            # get children for the last item in a list
            children = NavItem.objects.filter(nav=self.nav,
                level = self.level+1,
                ordering__gt=self.ordering).order_by('ordering')
            return children
    
    @property
    def next(self):
        try:
            next = NavItem.objects.get(ordering=self.ordering+1, nav=self.nav)
        except NavItem.DoesNotExist:
            return None
        return next
        
    @property
    def prev(self):
        try:
            prev = NavItem.objects.get(ordering=self.ordering-1, nav=self.nav)
        except NavItem.DoesNotExist:
            return None
        return prev
    
    @property
    def next_range(self):
        if self.next:
            next = range(0, self.next.level-self.level)
        else:
            #first item
            next = range(0, self.level+1)
        return next
        
    @property
    def prev_range(self):
        if self.prev:
            prev = range(0, self.prev.level-self.level)
        else:
            #last item
            prev = range(0, self.level+1)
        return prev
