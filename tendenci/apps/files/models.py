import hashlib
import os
import mimetypes
import uuid
from PIL import Image
import re
#from slate import PDF
import cStringIO
from base64 import b64encode

from django.db import models, connection
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ManyToOneRel

from tagging.fields import TagField
from tendenci.libs.boto_s3.utils import set_s3_file_permission
from tendenci.apps.notifications import models as notification
from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.utils import get_notice_recipients
from tendenci.apps.files.managers import FileManager
from tendenci.apps.base.utils import extract_pdf
from tendenci.apps.categories.models import CategoryItem
from tendenci.apps.site_settings.utils import get_setting


def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._-]+', '_', filename)
    m = hashlib.md5()
    m.update(filename)

    hex_digest = m.hexdigest()[:8]

    if instance.content_type:
        if hasattr(instance.content_type, '__call__'):
            content_type = instance.content_type()
        else:
            content_type = instance.content_type
        content_type = re.sub(r'[^a-zA-Z0-9._]+', '_', unicode(content_type))
        return 'files/%s/%s/%s' % (content_type, hex_digest, filename)

    return 'files/files/%s/%s' % (hex_digest, filename)


class File(TendenciBaseModel):
    file = models.FileField("", max_length=260, upload_to=file_directory)
    guid = models.CharField(max_length=40)
    name = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    # file type - image, video, or text...
    f_type = models.CharField(max_length=20, blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    group = models.ForeignKey(
        Group, null=True, default=get_default_group, on_delete=models.SET_NULL)
    tags = TagField(null=True, blank=True)
    categories = GenericRelation(CategoryItem, object_id_field="object_id", content_type_field="content_type")

    file_cat = models.ForeignKey('FilesCategory', verbose_name=_("Files Category"),
                                 related_name="file_cat", null=True, on_delete=models.SET_NULL)
    file_sub_cat = models.ForeignKey('FilesCategory', verbose_name=_("Files Sub Category"),
                                     related_name="file_subcat", null=True, on_delete=models.SET_NULL)

    perms = GenericRelation(
        ObjectPermission,
        object_id_field="object_id",
        content_type_field="content_type")

    objects = FileManager()

    class Meta:
        permissions = (("view_file", _("Can view file")),)
        app_label = 'files'

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)

        self._originaldict = {}
        for field_name in self._meta.get_all_field_names():

            if isinstance(self._meta.get_field_by_name(field_name)[0], ManyToOneRel):
                continue  # preventing circular reference

            if hasattr(self, field_name):
                value = getattr(self, field_name)
                # skip Manager type objects
                if not isinstance(value, models.Manager):
                    self._originaldict[field_name] = value

    def has_changed(self):
        """
        Loop through key fields and return True
        if a key field has changed.
        """
        for field_name in self._originaldict.keys():
            if getattr(self, field_name) != self._originaldict[field_name]:
                return True

        return False


    @models.permalink
    def get_absolute_url(self):
        return ("file", [self.pk])

    @models.permalink
    def get_absolute_download_url(self):
        return ("file", [self.pk, 'download'])

    def __unicode__(self):
        return self.get_name()

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
        created = False
        if not self.id:
            self.guid = unicode(uuid.uuid1())
            created = True
        self.f_type = self.type()

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

        # send notification to administrator(s) and module recipient(s)
        if created:
            recipients = get_notice_recipients('module', 'files', 'filerecipients')
            site_display_name = get_setting('site', 'global', 'sitedisplayname')
            site_url = get_setting('site', 'global', 'siteurl')
            if recipients and notification:

                notification_params = {
                    'object': self,
                    'SITE_GLOBAL_SITEDISPLAYNAME': site_display_name,
                    'SITE_GLOBAL_SITEURL': site_url,
                }

                if self.owner:
                    notification_params['author'] = self.owner.get_full_name() or self.owner

                notification.send_emails(recipients, 'file_added', notification_params)

    def delete(self, *args, **kwargs):
        # Related objects
        # Import related objects here to prevent circular references
        from tendenci.apps.pages.models import Page
        from tendenci.apps.events.models import Event
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
        #connection._rollback()    # comment it out because this line of code leads to IntegrityError for files that inherit File's model.

        # send notification to administrator(s) and module recipient(s)
        if self.file:
            recipients = get_notice_recipients('module', 'files', 'filerecipients')
            site_display_name = get_setting('site', 'global', 'sitedisplayname')
            if self.owner:
                owner = self.owner.get_full_name() or self.owner
            else:
                owner = "Unknown"

            if recipients and notification:
                notification.send_emails(recipients, 'file_deleted', {
                    'object': self,
                    'author': owner,
                    'SITE_GLOBAL_SITEDISPLAYNAME': site_display_name,
                })

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
            'image': ('.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff', '.bmp'),
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
        
    def get_size(self):
        try:
            return self.file.size
        except:
            return 0

    def read(self):
        """Returns a file's text data
        For now this only considers pdf files.
        if the file cannot be read this will return an empty string.
        """

        if not settings.USE_S3_STORAGE:
            if not os.path.exists(self.file.path):
                return unicode()

        if settings.INDEX_FILE_CONTENT:
            if self.type() == 'pdf':

                try:
                    return extract_pdf(self.file.file)
                except:
                    return unicode()

        return unicode()

    def is_public_file(self):
        return all([
            self.is_public,
            self.allow_anonymous_view,
            self.status,
            self.status_detail.lower() == "active"])

    def get_file_public_url(self):
        if self.is_public_file():
            if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                return self.file.url
            else:
                return "%s%s" % (settings.MEDIA_URL, self.file)
        return None

    def get_content(self):
        if self.content_type and self.object_id:
            try:
                model = self.content_type.model_class()
                return model.objects.get(pk=self.object_id)
            except:
                return None
        else:
            for r_object in self._meta.get_all_related_objects():
                if hasattr(self, r_object.name):
                    return getattr(self, r_object.name)
            return None

    def get_binary(self, **kwargs):
        """
        Returns binary in encoding base64.
        """
        from tendenci.apps.files.utils import build_image
        size = kwargs.get('size') or self.image_dimensions()

        binary = build_image(self.file, size, 'FILE_IMAGE_PRE_KEY')
        return b64encode(binary)


class MultipleFile(models.Model):
    """
    Dummy model to enable us of having an admin options in the
    Files section to add multiple files
    """
    class Meta:
        managed = False
        app_label = 'files'


# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `File` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class FilesCategory(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True)

    class Meta:
        verbose_name_plural = _("File Categories")
        ordering = ('name',)
        app_label = 'files'

    def __unicode__(self):
        return self.name
