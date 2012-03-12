import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from base.fields import SlugField
from perms.models import TendenciBaseModel
from pages.managers import PageManager
from tinymce import models as tinymce_models
from meta.models import Meta as MetaTags
from entities.models import Entity
from pages.module_meta import PageMeta
from categories.models import CategoryItem
from perms.object_perms import ObjectPermission

class Page(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=500, blank=True)
    slug = SlugField(_('URL Path'), unique=True)  
    content = tinymce_models.HTMLField()
    view_contact_form = models.BooleanField()
    design_notes = models.TextField(_('Design Notes'), blank=True)
    syndicate = models.BooleanField(_('Include in RSS feed'))
    template = models.CharField(_('Template'), max_length=50, blank=True)
    tags = TagField(blank=True)
    
    objects = PageManager()
    entity = models.ForeignKey(Entity,null=True)
    # html-meta tags
    meta = models.OneToOneField(MetaTags, null=True)
    
    categories = generic.GenericRelation(CategoryItem,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    class Meta:
        permissions = (("view_page","Can view page"),)

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return PageMeta().get_meta(self, name)
    
    @models.permalink
    def get_absolute_url(self):
        return ("page", [self.slug])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            
        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title
    
    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category__name', 'parent__name'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items
