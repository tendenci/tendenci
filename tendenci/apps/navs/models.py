from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.pages.models import Page
from tendenci.apps.navs.managers import NavManager
from tendenci.apps.navs.signals import update_nav_links
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.navs.utils import clear_nav_cache

class Nav(TendenciBaseModel):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    megamenu = models.BooleanField(default=False)

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = NavManager()

    class Meta:
#         permissions = (("view_nav",_("Can view nav")),)
        app_label = 'navs'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('navs.detail', args=[self.pk])

    def save(self, *args, **kwargs):
        super(Nav, self).save(*args, **kwargs)
        # reset nav cache
        clear_nav_cache(self)

    @property
    def top_items(self):
        """
        Returns all items with level 0.
        """
        return self.navitem_set.filter(level=0).order_by('position')

class NavItem(OrderingBaseModel):
    nav = models.ForeignKey(Nav, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    title = models.CharField(_("Title Attribute"), max_length=100, blank=True, null=True)
    new_window = models.BooleanField(_("Open in a new window"), default=False)
    css = models.CharField(_("CSS Class"), max_length=100, blank=True, null=True)
    level = models.IntegerField(default=0)
    page = models.ForeignKey(Page, null=True, on_delete=models.CASCADE)
    url = models.CharField(_("URL"), max_length=200, blank=True, null=True)

    class Meta:
        app_label = 'navs'

    def __str__(self):
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
        level = self.level or 0
        level_down = level + 1
        position = self.position or 0

        # get the first sibling among the ones with greater ordering
        siblings = NavItem.objects.filter(
            nav=self.nav,
            position__gt=position,
            level=level
        ).order_by('position')
        if siblings:
            sibling = siblings[0]
            sibling_position = sibling.position or 0
            # return all the items between the adjacent siblings.
            children = NavItem.objects.filter(
                nav=self.nav,
                level=level_down,
                position__gt=position,
                position__lt=sibling_position
            ).order_by('position')
            return children
        else:
            # get children for the last item in a list
            children = NavItem.objects.filter(
                nav=self.nav,
                level=level_down,
                position__gt=position
            ).order_by('position')
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
        return list(next)

    @property
    def prev_range(self):
        if self.prev:
            prev = range(0, self.prev.level-self.level)
        else:
            #last item
            prev = range(0, self.level+1)
        return list(prev)

# Update page nav items when a page is saved
models.signals.post_save.connect(update_nav_links, sender=Nav)
