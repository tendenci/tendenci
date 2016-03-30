import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse

from tagging.fields import TagField
from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.categories.models import CategoryItem

from tendenci.apps.base.fields import SlugField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.files.models import File
from tendenci.apps.user_groups.utils import get_default_group
from tendenci.apps.pages.managers import PageManager
from tendenci.apps.pages.module_meta import PageMeta
from tendenci.apps.user_groups.models import Group
from tendenci.libs.boto_s3.utils import set_s3_file_permission


class BasePage(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=500, blank=True)
    slug = SlugField(_('URL Path'))
    header_image = models.ForeignKey('HeaderImage', null=True)
    content = tinymce_models.HTMLField()
    view_contact_form = models.BooleanField(default=False)
    design_notes = models.TextField(_('Design Notes'), blank=True)
    syndicate = models.BooleanField(_('Include in RSS feed'), default=False)
    template = models.CharField(_('Template'), max_length=50, blank=True)
    tags = TagField(blank=True)
    meta = models.OneToOneField(MetaTags, null=True)
    categories = GenericRelation(CategoryItem,
        object_id_field="object_id", content_type_field="content_type")

    class Meta:
        abstract = True
        app_label = 'pages'

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
    CONTRIBUTOR_AUTHOR = 1
    CONTRIBUTOR_PUBLISHER = 2
    CONTRIBUTOR_CHOICES = ((CONTRIBUTOR_AUTHOR, _('Author')),
                           (CONTRIBUTOR_PUBLISHER, _('Publisher')))

    group = models.ForeignKey(Group, null=True, default=get_default_group)
    contributor_type = models.IntegerField(choices=CONTRIBUTOR_CHOICES,
                                           default=CONTRIBUTOR_AUTHOR)
    google_profile = models.URLField(_('Google+ URL'), blank=True)
    perms = GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")
    objects = PageManager()

    class Meta:
        permissions = (("view_page", _("Can view page")),)
        app_label = 'pages'

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

    @property
    def has_google_author(self):
        return self.contributor_type == self.CONTRIBUTOR_AUTHOR

    @property
    def has_google_publisher(self):
        return self.contributor_type == self.CONTRIBUTOR_PUBLISHER


class HeaderImage(File):
    pass

    class Meta:
        app_label = 'pages'
