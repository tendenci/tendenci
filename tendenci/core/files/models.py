import os
import mimetypes
import uuid
import Image
import re
from slate import PDF
import urllib
import cStringIO

from django.db import models, connection
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.contrib.contenttypes import generic
from django.core.files.storage import default_storage

from tagging.fields import TagField

from tendenci.libs.boto_s3.utils import set_s3_file_permission

from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.files.managers import FileManager
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.categories.models import CategoryItem

from tendenci.apps.redirects.models import Redirect
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404


def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    uuid_hex = uuid.uuid1().get_hex()[:8]

    if instance.content_type:
        content_type = re.sub(r'[^a-zA-Z0-9._]+', '-', unicode(instance.content_type))
        return 'files/%s/%s/%s' % (content_type, uuid_hex, filename)

    return 'files/files/%s/%s' % (uuid_hex, filename)


class File(TendenciBaseModel):
    file = models.FileField("", max_length=260, upload_to=file_directory)
    guid = models.CharField(max_length=40)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    group = models.ForeignKey(Group, null=True,
        default=get_default_group, on_delete=models.SET_NULL)
    tags = TagField(null=True, blank=True)
    categories = generic.GenericRelation(CategoryItem, object_id_field="object_id", content_type_field="content_type")

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = FileManager()

    class Meta:
        permissions = (("view_file", "Can view file"),)

    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category__name', 'parent__name'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = unicode(uuid.uuid1())

        super(File, self).save(*args, **kwargs)

        if self.is_public_file():
            set_s3_file_permission(self.file, public=True)
        else:
            set_s3_file_permission(self.file, public=False)
            cache_set = cache.get("files_cache_set.%s" % self.pk)
            if cache_set is not None:
                # TODO remove cached images
                cache.delete_many(cache.get("files_cache_set.%s" % self.pk))
                cache.delete("files_cache_set.%s" % self.pk)

    def delete(self, *args, **kwargs):
        # Related objects
        # Import related objects here to prevent circular references
        from tendenci.apps.pages.models import Page
        from tendenci.addons.events.models import Event
        from tendenci.apps.stories.models import Story
        pages = Page.objects.filter(header_image=self.pk)
        events = Event.objects.filter(image=self.pk)
        stories = Story.objects.filter(image=self.pk)
        # Set foreign key of related objects to None
        for page in pages:
            page.header_image = None
            page.save()
        for event in events:
            event.image = None
            event.save()
        for story in stories:
            story.image = None
            story.save()

        # roll back the transaction to fix the error for postgresql
        #"current transaction is aborted, commands ignored until 
        # end of transaction block"
        connection._rollback()

        # delete actual file; do not save() self.instance
        self.file.delete(save=False)

        # delete database record
        super(File, self).delete(*args, **kwargs)

    def basename(self):
        return os.path.basename(unicode(self.file.name))

    def ext(self):
        return os.path.splitext(self.basename())[-1]

    def get_name(self):
        return self.name or os.path.splitext(self.basename())[0]

    def get_name_ext(self):
        return "%s%s" % (self.get_name(), self.ext())

    def type(self):
        ext = self.ext().lower()

        # map file-type to extension
        types = {
            'image': ('.jpg', '.jpeg', '.gif', '.png', 
                      '.tif', '.tiff', '.bmp'),
            'text': ('.txt', '.doc', '.docx'),
            'spreadsheet': ('.csv', '.xls', '.xlsx'),
            'powerpoint': ('.ppt', '.pptx'),
            'pdf': ('.pdf'),
            'video': ('.wmv', '.mov', '.mpg', '.mp4', '.m4v'),
            'zip': ('.zip'),
        }

        # if file ext. is recognized
        # return icon
        for type in types:
            if ext in types[type]:
                return type

        return None

    def mime_type(self):
        types = {  # list of uncommon mimetypes
            'application/msword': ('.doc', '.docx'),
            'application/ms-powerpoint': ('.ppt', '.pptx'),
            'application/ms-excel': ('.xls', '.xlsx'),
            'video/x-ms-wmv': ('.wmv'),
        }
        # add mimetypes
        for type in types:
            for ext in types[type]:
                mimetypes.add_type(type, ext)
        # guess mimetype
        mimetype = mimetypes.guess_type(self.file.name)[0]
        return mimetype

    def icon(self):

        # if we don't know the type
        # we can't find an icon [to represent the file]
        if not self.type():
            return None

        # assign icons directory
        icons_dir = os.path.join(settings.LOCAL_STATIC_URL, 'images/icons')

        # map file-type to image file
        icons = {
            'text': 'icon-ms-word-2007.gif',
            'spreadsheet': 'icon-ms-excel-2007.gif',
            'powerpoint': 'icon-ms-powerpoint-2007.gif',
            'image': 'icon-ms-image-2007.png',
            'pdf': 'icon-pdf.png',
            'video': 'icon-wmv.png',
            'zip': 'icon-zip.gif',
        }

        # return image path
        return icons_dir + '/' + icons[self.type()]

    def get_file_from_remote_storage(self):
        return cStringIO.StringIO(default_storage.open(self.file.name).read())

    def image_dimensions(self):
        try:
            if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                im = Image.open(self.get_file_from_remote_storage())
            else:
                im = Image.open(self.file.path)
            return im.size
        except Exception:
            return (0, 0)

    def read(self):
        """Returns a file's text data
        For now this only considers pdf files.
        if the file cannot be read this will return an empty string.
        """

        if not settings.USE_S3_STORAGE:
            if not os.path.exists(self.file.path):
                return unicode()

        if self.type() == 'pdf':

            try:
                doc = PDF(self.file.file)
            except:
                return unicode()

            return doc.text()

        return unicode()

    @models.permalink
    def get_absolute_url(self):
        return ("file", [self.pk])

    @models.permalink
    def get_absolute_download_url(self):
        return ("file", [self.pk, 'download'])

    def __unicode__(self):
        return self.get_name()

    def is_public_file(self):
        return all([self.is_public,
            self.allow_anonymous_view,
            self.status,
            self.status_detail.lower() == "active"]
            )

    def get_file_public_url(self):
        if self.is_public_file():
            if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                return self.file.url
            else:
                return "%s%s" % (settings.MEDIA_URL, self.file)
        return None
