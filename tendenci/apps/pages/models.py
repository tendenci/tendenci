import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

from tagging.fields import TagField
from tinymce import models as tinymce_models
from tendenci.core.meta.models import Meta as MetaTags
from tendenci.core.categories.models import CategoryItem

from tendenci.core.base.fields import SlugField
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.files.models import File

from tendenci.apps.pages.managers import PageManager
from tendenci.apps.pages.module_meta import PageMeta
from tendenci.libs.boto_s3.utils import set_s3_file_permission


class BasePage(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=500, blank=True)
    slug = SlugField(_('URL Path'))
    header_image = models.ForeignKey('HeaderImage', null=True)
    content = tinymce_models.HTMLField()
    view_contact_form = models.BooleanField()
    design_notes = models.TextField(_('Design Notes'), blank=True)
    syndicate = models.BooleanField(_('Include in RSS feed'))
    template = models.CharField(_('Template'), max_length=50, blank=True)
    tags = TagField(blank=True)
    meta = models.OneToOneField(MetaTags, null=True)
    categories = generic.GenericRelation(CategoryItem,
        object_id_field="object_id", content_type_field="content_type")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid1())
        super(BasePage, self).save(*args, **kwargs)
        if self.header_image:
            if self.is_public():
                set_s3_file_permission(self.header_image.file, public=True)
            else:
                set_s3_file_permission(self.header_image.file, public=False)

    def __unicode__(self):
        return self.title

    def get_header_image_url(self):
        if not self.header_image:
            return ''

        if self.is_public():
            return self.header_image.file.url

        return reverse('page.header_image', args=[self.id])

    def is_public(self):
        return all([self.allow_anonymous_view,
                self.status,
                self.status_detail in ['active']])

    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category__name', 'parent__name'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items

    @property
    def version(self):
        if self.status and self.status_detail:
            return self.status_detail + '-' + str(self.pk) + ' ' + str(self.create_dt)
        elif not self.status:
            return 'deleted-' + str(self.pk) + ' ' + str(self.create_dt)
        return ''


class Page(BasePage):
    perms = generic.GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")
    objects = PageManager()

    class Meta:
        permissions = (("view_page", "Can view page"),)

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

    @models.permalink
    def get_version_url(self, hash):
        return ("page.version", [hash])


class HeaderImage(File):
    pass
