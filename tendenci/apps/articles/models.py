import uuid
from datetime import datetime
from django.db import models
from django.urls import reverse
from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings

from tagging.fields import TagField
from timezone_field import TimeZoneField

from tendenci.apps.base.fields import SlugField
from tendenci.apps.base.utils import adjust_datetime_to_timezone, get_timezone_choices
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.categories.models import CategoryItem
from tendenci.apps.articles.managers import ArticleManager
from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.articles.module_meta import ArticleMeta
from tendenci.apps.files.models import File


class Article(TendenciBaseModel):
    CONTRIBUTOR_AUTHOR = 1
    CONTRIBUTOR_PUBLISHER = 2
    CONTRIBUTOR_CHOICES = ((CONTRIBUTOR_AUTHOR, _('Author')),
                           (CONTRIBUTOR_PUBLISHER, _('Publisher')))

    guid = models.CharField(max_length=40)
    slug = SlugField(_('URL Path'), unique=True)
    timezone = TimeZoneField(verbose_name=_('Time Zone'), default='US/Central', choices=get_timezone_choices(), max_length=100)
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    body = tinymce_models.HTMLField()
    source = models.CharField(max_length=300, blank=True)
    first_name = models.CharField(_('First Name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=100, blank=True)
    contributor_type = models.IntegerField(choices=CONTRIBUTOR_CHOICES,
                                           default=CONTRIBUTOR_AUTHOR)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)
    thumbnail = models.ForeignKey(File, null=True,
                                  on_delete=models.SET_NULL,
                                  help_text=_('The thumbnail image can be used on your homepage ' +
                                 'or sidebar if it is setup in your theme. The thumbnail image ' +
                                 'will not display on the news page.'))
    release_dt = models.DateTimeField(_('Release Date/Time'), null=True, blank=True)
    # used for better performance when retrieving a list of released articles
    release_dt_local = models.DateTimeField(null=True, blank=True)
    syndicate = models.BooleanField(_('Include in RSS feed'), default=True)
    featured = models.BooleanField(default=False)
    design_notes = models.TextField(_('Design Notes'), blank=True)
    group = models.ForeignKey(Group, null=True, default=get_default_group, on_delete=models.SET_NULL)
    tags = TagField(blank=True)

    # for podcast feeds
    enclosure_url = models.CharField(_('Enclosure URL'), max_length=500, blank=True)
    enclosure_type = models.CharField(_('Enclosure Type'), max_length=120, blank=True)
    enclosure_length = models.IntegerField(_('Enclosure Length'), default=0)

    not_official_content = models.BooleanField(_('Official Content'), blank=True, default=True)

    # html-meta tags
    meta = models.OneToOneField(MetaTags, null=True, on_delete=models.SET_NULL)

    categories = GenericRelation(CategoryItem,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = ArticleManager()

    class Meta:
#         permissions = (("view_article", _("Can view article")),)
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        app_label = 'articles'

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        methods coupled to this instance.
        """
        return ArticleMeta().get_meta(self, name)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])

    def get_version_url(self, hash):
        return reverse('article.version', args=[hash])

    def __str__(self):
        return self.headline

    def get_thumbnail_url(self):
        if not self.thumbnail:
            return u''

        return reverse('file', args=[self.thumbnail.pk])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())
        self.assign_release_dt_local()
        super(Article, self).save(*args, **kwargs)

    def assign_release_dt_local(self):
        """
        convert release_dt to the corresponding local time

        example:

        if
            release_dt: 2014-05-09 03:30:00
            timezone: US/Pacific
            settings.TIME_ZONE: US/Central
        then
            the corresponding release_dt_local will be: 2014-05-09 05:30:00
        """
        now = datetime.now()
        now_with_tz = adjust_datetime_to_timezone(now, settings.TIME_ZONE)
        if self.timezone and self.release_dt and self.timezone.zone != settings.TIME_ZONE:
            time_diff = adjust_datetime_to_timezone(now, self.timezone) - now_with_tz
            self.release_dt_local = self.release_dt + time_diff
        else:
            self.release_dt_local = self.release_dt

    def age(self):
        return datetime.now() - self.create_dt

    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category', 'parent'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items

    @property
    def has_google_author(self):
        return self.contributor_type == self.CONTRIBUTOR_AUTHOR

    @property
    def has_google_publisher(self):
        return self.contributor_type == self.CONTRIBUTOR_PUBLISHER
