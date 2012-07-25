import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from tinymce import models as tinymce_models
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.categories.models import CategoryItem

from tendenci.apps.base.fields import SlugField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.entities.models import Entity
from tendenci.apps.files.models import File

from tendenci.apps.pages.managers import PageManager
from tendenci.apps.pages.module_meta import PageMeta

class Page(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=500, blank=True)
    slug = SlugField(_('URL Path'), unique=True)
    header_image = models.ForeignKey('HeaderImage', null=True)
    content = tinymce_models.HTMLField()
    view_contact_form = models.BooleanField()
    design_notes = models.TextField(_('Design Notes'), blank=True)
    syndicate = models.BooleanField(_('Include in RSS feed'))
    template = models.CharField(_('Template'), max_length=50, blank=True)
    tags = TagField(blank=True)
    entity = models.ForeignKey(Entity,null=True)
    # html-meta tags
    meta = models.OneToOneField(MetaTags, null=True)
    categories = generic.GenericRelation(CategoryItem,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    objects = PageManager()
    
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

class HeaderImage(File):
    pass
