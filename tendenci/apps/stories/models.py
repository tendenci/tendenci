from builtins import str
import uuid

from urllib.parse import urlparse

from django.db import models
from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType

from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.categories.models import CategoryItem
from tendenci.apps.site_settings.utils import get_setting
from tagging.fields import TagField
from tendenci.apps.files.models import File
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.stories.managers import StoryManager
from tendenci.libs.abstracts.models import OrderingBaseModel


class StoryPhoto(File):
    class Meta:
        app_label = 'stories'
        manager_inheritance_from_future = True


class Story(OrderingBaseModel, TendenciBaseModel):
    """
    A Story is used across a site to add linked image content to a specific design area.
    The basic features of a Story include:

    - Title
    - Description (accepts HTML)
    - Image
    - Link

    Stories also include tags and a start and end time for automatic expiration.

    Stories use the Tendenci Base Model.
    """

    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    syndicate = models.BooleanField(_('Include in RSS feed'), default=False)
    full_story_link = models.CharField(_('Full Story Link'), max_length=300, blank=True)
    link_title = models.CharField(_('Link Title'), max_length=200, blank=True)
    video_embed_url = models.URLField(_('Embed URL'), blank=True, null=True,
                                      help_text=_('Embed URL for a Youtube or Vimeo video'))
    start_dt = models.DateTimeField(_('Start Date/Time'), null=True, blank=True)
    end_dt = models.DateTimeField(_('End Date/Time'), null=True, blank=True)
    expires = models.BooleanField(_('Expires'), default=True)
    image = models.ForeignKey(
        StoryPhoto,
        help_text=_('Photo that represents this story.'),
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(Group, null=True, default=get_default_group, on_delete=models.SET_NULL)
    tags = TagField(blank=True, default='')

    rotator = models.ForeignKey('Rotator', null=True, default=None, blank=True,
        help_text=_('The rotator where this story belongs.'), on_delete=models.CASCADE)
    rotator_position = models.IntegerField(_('Rotator Position'), default=0, blank=True)

    categories = GenericRelation(CategoryItem,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = StoryManager()

    class Meta:
#         permissions = (("view_story", _("Can view story")),)
        verbose_name_plural = _("stories")
        ordering = ['position']
        app_label = 'stories'

    def __str__(self):
        return self.title

    @property
    def content_type(self):
        return 'stories'

    def photo(self):
        if self.image and self.image.file:
            return self.image.file

        return None

    def get_absolute_url(self):
        from django.urls import reverse
        url = reverse("story", args=[self.pk])
        if self.full_story_link:
            url = self.full_story_link
            o = urlparse(url)

            if not o.scheme:  # if relative URL
                url = '%s%s' % (get_setting('site', 'global', 'siteurl'), url)

        return url

    def save(self, *args, **kwargs):
        self.guid = self.guid or str(uuid.uuid4())
        photo_upload = kwargs.pop('photo', None)

        if self.pk is None:
            # Append to top of the list on add
            try:
                last = Story.objects.all().order_by('-position')[0]
                if last.position:
                    self.position = int(last.position) + 1
                else:
                    self.position = 1
            except IndexError:
                # First row
                self.position = 1
                pass

        super(Story, self).save(*args, **kwargs)

        if photo_upload and self.pk:
            image = StoryPhoto(
                content_type=ContentType.objects.get_for_model(self.__class__),
                object_id=self.pk,
                creator=self.creator,
                creator_username=self.creator_username,
                owner=self.owner,
                owner_username=self.owner_username
            )
            photo_upload.file.seek(0)
            image.file.save(photo_upload.name, photo_upload)  # save file row
            image.save()  # save image row

            if self.image:
                self.image.delete()  # delete image and file row
            self.image = image  # set image

            self.save()

    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category', 'parent'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items


class Rotator(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        app_label = 'stories'

    def __str__(self):
        return self.name
