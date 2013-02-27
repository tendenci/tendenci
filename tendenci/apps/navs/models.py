from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.apps.pages.models import Page
from tendenci.apps.navs.managers import NavManager
from tendenci.libs.abstracts.models import OrderingBaseModel

class Nav(TendenciBaseModel):
    class Meta:
        permissions = (("view_nav","Can view nav"),)
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    megamenu = models.BooleanField(default=False)

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

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
        return self.navitem_set.filter(level=0).order_by('position')
    
class NavItem(OrderingBaseModel):
    nav = models.ForeignKey(Nav)
    label = models.CharField(max_length=100)
    title = models.CharField(_("Title Attribute"), max_length=100, blank=True, null=True)
    new_window = models.BooleanField(_("Open in a new window"), default=False)
    css = models.CharField(_("CSS Class"), max_length=100, blank=True, null=True)
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
            position__gt=self.position,
            level=self.level).order_by('position')
        if siblings:
            sibling = siblings[0]
            #return all the items between the adjacent siblings.
            children = NavItem.objects.filter(nav=self.nav,
                level = self.level+1,
                position__gt=self.position,
                position__lt=sibling.position).order_by('position')
            return children
        else:
            # get children for the last item in a list
            children = NavItem.objects.filter(nav=self.nav,
                level = self.level+1,
                position__gt=self.position).order_by('position')
            return children
    
    @property
    def next(self):
        try:
            next = NavItem.objects.get(position=self.position+1, nav=self.nav)
        except NavItem.DoesNotExist:
            return None
        return next
        
    @property
    def prev(self):
        try:
            prev = NavItem.objects.get(position=self.position-1, nav=self.nav)
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
