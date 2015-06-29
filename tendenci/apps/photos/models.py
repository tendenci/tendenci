import uuid
import os
from PIL import Image as PILImage
from PIL.ExifTags import TAGS as PILTAGS
from PIL import ImageFile
from PIL import ImageFilter

from datetime import datetime
from inspect import isclass
from cStringIO import StringIO

from django.db import models
from django.db.models.signals import post_init
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import SuspiciousOperation
from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import smart_str, force_unicode
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _
import simplejson
import requests

from tagging.fields import TagField

from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.base.fields import DictField
from tendenci.apps.photos.managers import PhotoManager, PhotoSetManager
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.photos.module_meta import PhotoMeta
from tendenci.libs.boto_s3.utils import set_s3_file_permission
from tendenci.libs.abstracts.models import OrderingBaseModel

from tendenci.apps.photos.utils import EXIF
from tendenci.apps.photos.utils.reflection import add_reflection
from tendenci.apps.photos.utils.watermark import apply_watermark
from tendenci.libs.abstracts.models import OrderingBaseModel

# max_length setting for the ImageModel ImageField
IMAGE_FIELD_MAX_LENGTH = getattr(settings, 'PHOTOS_IMAGE_FIELD_MAX_LENGTH', 100)

# Path to sample image
SAMPLE_IMAGE_PATH = getattr(settings, 'SAMPLE_IMAGE_PATH', os.path.join(os.path.dirname(__file__), 'res', 'sample.jpg'))  # os.path.join(settings.PROJECT_PATH, 'photos', 'res', 'sample.jpg'

# Modify image file buffer size.
ImageFile.MAXBLOCK = getattr(settings, 'PHOTOS_MAXBLOCK', 256 * 2 ** 10)

PHOTOS_DIR = settings.MEDIA_URL


def get_storage_path(instance, filename):
    # AWS S3 max key length: 260 characters
    return os.path.join('photos', uuid.uuid1().get_hex()[:8], filename)

# Quality options for JPEG images
JPEG_QUALITY_CHOICES = (
    (30, _('Very Low')),
    (40, _('Low')),
    (50, _('Medium-Low')),
    (60, _('Medium')),
    (70, _('Medium-High')),
    (80, _('High')),
    (90, _('Very High')),
)

# choices for new crop_anchor field in Photo
CROP_ANCHOR_CHOICES = (
    ('top', _('Top')),
    ('right', _('Right')),
    ('bottom', _('Bottom')),
    ('left', _('Left')),
    ('center', _('Center (Default)')),
)

IMAGE_TRANSPOSE_CHOICES = (
    ('FLIP_LEFT_RIGHT', _('Flip left to right')),
    ('FLIP_TOP_BOTTOM', _('Flip top to bottom')),
    ('ROTATE_90', _('Rotate 90 degrees counter-clockwise')),
    ('ROTATE_270', _('Rotate 90 degrees clockwise')),
    ('ROTATE_180', _('Rotate 180 degrees')),
)

WATERMARK_STYLE_CHOICES = (
    ('tile', _('Tile')),
    ('scale', _('Scale')),
)

# Prepare a list of image filters
filter_names = []
for n in dir(ImageFilter):
    klass = getattr(ImageFilter, n)
    if isclass(klass) and issubclass(klass, ImageFilter.BuiltinFilter) and \
        hasattr(klass, 'name'):
            filter_names.append(klass.__name__)
IMAGE_FILTERS_HELP_TEXT = _('Chain multiple filters using the following pattern "FILTER_ONE->FILTER_TWO->FILTER_THREE". Image filters will be applied in order. The following filters are available: %s.' % (', '.join(filter_names)))


class ImageModel(models.Model):
    image = models.ImageField(_('image'), max_length=IMAGE_FIELD_MAX_LENGTH, upload_to=get_storage_path)
    date_taken = models.DateTimeField(_('date taken'), null=True, blank=True, editable=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    crop_from = models.CharField(_('crop from'), blank=True, max_length=10, default='center', choices=CROP_ANCHOR_CHOICES)
    effect = models.ForeignKey('PhotoEffect', null=True, blank=True, related_name="%(class)s_related", verbose_name=_('effect'))

    class Meta:
        abstract = True

    def EXIF(self):
        try:
            content = default_storage.open(unicode(self.image)).read()
            im = PILImage.open(StringIO(content))
        except IOError:
            return

        try:
            return EXIF.process_file(im)
        except:
            try:
                return EXIF.process_file(im, details=False)
            except:
                return {}

    def admin_thumbnail(self):
        func = getattr(self, 'get_admin_thumbnail_url', None)
        if func is None:
            return _('An "admin_thumbnail" photo size has not been defined.')
        else:
            if hasattr(self, 'get_absolute_url'):
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.get_absolute_url(), func())
            else:
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.image.url, func())
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    def cache_path(self):
        # example 'photos/cache/3949a2d9' or 'photos/cache'
        l = unicode(self.image).split('/')
        l.insert(1, 'cache')
        return os.path.dirname('/'.join(l))

    def cache_url(self):
        return os.path.join(settings.MEDIA_URL, self.cache_path())

    def image_filename(self):
        return os.path.basename(force_unicode(self.image))

    def _get_filename_for_size(self, size):
        size = getattr(size, 'name', size)
        base, ext = os.path.splitext(self.image_filename())
        return ''.join([base, '_', size, ext])

    def _get_SIZE_photosize(self, size):
        return PhotoSizeCache().sizes.get(size)

    def _get_SIZE_size(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        file_path = self._get_SIZE_filename(size)

        if not default_storage.exists(file_path):
            return 0
        try:
            return PILImage.open(default_storage.open(file_path)).size
        except:
            return 0

    def _get_SIZE_url(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        if photosize.increment_count:
            self.increment_count()
        return '/'.join([self.cache_url(), self._get_filename_for_size(photosize.name)])

    def _get_SIZE_filename(self, size):
        photosize = PhotoSizeCache().sizes.get(size)

        return smart_str(os.path.join(self.cache_path(),
            self._get_filename_for_size(photosize.name)))

    def increment_count(self):
        self.view_count += 1
        models.Model.save(self)

    def add_accessor_methods(self, *args, **kwargs):
        for size in PhotoSizeCache().sizes.keys():
            setattr(self, 'get_%s_size' % size,
                    curry(self._get_SIZE_size, size=size))
            setattr(self, 'get_%s_photosize' % size,
                    curry(self._get_SIZE_photosize, size=size))
            setattr(self, 'get_%s_url' % size,
                    curry(self._get_SIZE_url, size=size))
            setattr(self, 'get_%s_filename' % size,
                    curry(self._get_SIZE_filename, size=size))

    def size_exists(self, photosize):
        func = getattr(self, "get_%s_filename" % photosize.name, None)

        if func:
            try:
                return default_storage.exists(func())
            except SuspiciousOperation:
                pass

        return False

    def resize_image(self, im, photosize):
        cur_width, cur_height = im.size
        new_width, new_height = photosize.size
        if photosize.crop:
            ratio = max(float(new_width)/cur_width,float(new_height)/cur_height)
            x = (cur_width * ratio)
            y = (cur_height * ratio)
            xd = abs(new_width - x)
            yd = abs(new_height - y)
            x_diff = int(xd / 2)
            y_diff = int(yd / 2)
            if self.crop_from == 'top':
                box = (int(x_diff), 0, int(x_diff+new_width), new_height)
            elif self.crop_from == 'left':
                box = (0, int(y_diff), new_width, int(y_diff+new_height))
            elif self.crop_from == 'bottom':
                box = (int(x_diff), int(yd), int(x_diff+new_width), int(y)) # y - yd = new_height
            elif self.crop_from == 'right':
                box = (int(xd), int(y_diff), int(x), int(y_diff+new_height)) # x - xd = new_width
            else:
                box = (int(x_diff), int(y_diff), int(x_diff+new_width), int(y_diff+new_height))
            im = im.resize((int(x), int(y)), PILImage.ANTIALIAS).crop(box)
        else:
            if not new_width == 0 and not new_height == 0:
                ratio = min(float(new_width)/cur_width,
                            float(new_height)/cur_height)
            else:
                if new_width == 0:
                    ratio = float(new_height)/cur_height
                else:
                    ratio = float(new_width)/cur_width
            new_dimensions = (int(round(cur_width*ratio)),
                              int(round(cur_height*ratio)))
            if new_dimensions[0] > cur_width or \
               new_dimensions[1] > cur_height:
                if not photosize.upscale:
                    return im
            im = im.resize(new_dimensions, PILImage.ANTIALIAS)
        return im

    def create_size(self, photosize):
        from django.core.files.storage import default_storage

        if self.size_exists(photosize):
            return

        try:
            content = default_storage.open(unicode(self.image)).read()
            im = PILImage.open(StringIO(content))
        except IOError as e:
            print e
            return

        im_format = im.format

        # Apply effect if found
        if hasattr(self, 'effect') and self.effect is not None:
            im = self.effect.pre_process(im)
        elif hasattr(photosize, 'effect') and photosize.effect is not None:
            im = photosize.effect.pre_process(im)

        # Resize/crop image
        if im.size != photosize.size and photosize.size != (0, 0):
            im = self.resize_image(im, photosize)

        # Apply watermark if found
        if hasattr(photosize, 'watermark') and photosize.watermark is not None:
            im = photosize.watermark.post_process(im)

        # Save file
        im_filename = getattr(self, "get_%s_filename" % photosize.name)()

        try:
            import StringIO as StringIO2
            buffer = StringIO2.StringIO()
            im.save(buffer, im_format, quality=int(photosize.quality), optimize=True)
            default_storage.save(im_filename, ContentFile(buffer.getvalue()))
        except IOError as e:
            print e
            pass

    def remove_size(self, photosize, remove_dirs=True):
        if not self.size_exists(photosize):
            return
        filename = getattr(self, "get_%s_filename" % photosize.name)()
        if os.path.isfile(filename):
            os.remove(filename)
        if remove_dirs:
            self.remove_cache_dirs()

    def clear_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            self.remove_size(photosize, False)
        self.remove_cache_dirs()

    def pre_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            if photosize.pre_cache:
                self.create_size(photosize)

    def remove_cache_dirs(self):
        try:
            os.removedirs(self.cache_path())
        except:
            pass

    def save(self, *args, **kwargs):
        if self.date_taken is None:
            try:
                exif_date = self.EXIF.get('EXIF DateTimeOriginal', None)
                if exif_date is not None:
                    d, t = str.split(exif_date.values)
                    year, month, day = d.split(':')
                    hour, minute, second = t.split(':')
                    self.date_taken = datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(second))
            except:
                pass
        if self.date_taken is None:
            self.date_taken = datetime.now()
        if self._get_pk_val():
            self.clear_cache()
        super(ImageModel, self).save(*args, **kwargs)
        self.pre_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super(ImageModel, self).delete()


class BaseEffect(models.Model):
    name = models.CharField(_('name'), max_length=30, unique=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        abstract = True

    def sample_dir(self):
        return os.path.join(settings.MEDIA_ROOT, PHOTOS_DIR, 'samples')

    def sample_url(self):
        return settings.MEDIA_URL + '/'.join([PHOTOS_DIR, 'samples', '%s %s.jpg' % (self.name.lower(), 'sample')])

    def sample_filename(self):
        return os.path.join(self.sample_dir(), '%s %s.jpg' % (self.name.lower(), 'sample'))

    def create_sample(self):
        if not os.path.isdir(self.sample_dir()):
            os.makedirs(self.sample_dir())
        try:
            im = PILImage.open(SAMPLE_IMAGE_PATH)
        except IOError:
            raise IOError('Photos was unable to open the sample image: %s.' % SAMPLE_IMAGE_PATH)
        im = self.process(im)
        im.save(self.sample_filename(), 'JPEG', quality=90, optimize=True)

    def admin_sample(self):
        return u'<img src="%s">' % self.sample_url()
    admin_sample.short_description = 'Sample'
    admin_sample.allow_tags = True

    def pre_process(self, im):
        return im

    def post_process(self, im):
        return im

    def process(self, im):
        im = self.pre_process(im)
        im = self.post_process(im)
        return im

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        try:
            os.remove(self.sample_filename())
        except:
            pass
        models.Model.save(self, *args, **kwargs)
        self.create_sample()
        for size in self.photo_sizes.all():
            size.clear_cache()
        # try to clear all related subclasses of ImageModel
        for prop in [prop for prop in dir(self) if prop[-8:] == '_related']:
            for obj in getattr(self, prop).all():
                obj.clear_cache()
                obj.pre_cache()

    def delete(self):
        try:
            os.remove(self.sample_filename())
        except:
            pass
        models.Model.delete(self)


class PhotoEffect(BaseEffect):
    """ A pre-defined effect to apply to photos """
    transpose_method = models.CharField(_('rotate or flip'), max_length=15, blank=True, choices=IMAGE_TRANSPOSE_CHOICES)
    color = models.FloatField(_('color'), default=1.0, help_text=_("A factor of 0.0 gives a black and white image, a factor of 1.0 gives the original image."))
    brightness = models.FloatField(_('brightness'), default=1.0, help_text=_("A factor of 0.0 gives a black image, a factor of 1.0 gives the original image."))
    contrast = models.FloatField(_('contrast'), default=1.0, help_text=_("A factor of 0.0 gives a solid grey image, a factor of 1.0 gives the original image."))
    sharpness = models.FloatField(_('sharpness'), default=1.0, help_text=_("A factor of 0.0 gives a blurred image, a factor of 1.0 gives the original image."))
    filters = models.CharField(_('filters'), max_length=200, blank=True, help_text=_(IMAGE_FILTERS_HELP_TEXT))
    reflection_size = models.FloatField(_('size'), default=0, help_text=_("The height of the reflection as a percentage of the orignal image. A factor of 0.0 adds no reflection, a factor of 1.0 adds a reflection equal to the height of the orignal image."))
    reflection_strength = models.FloatField(_('strength'), default=0.6, help_text=_("The initial opacity of the reflection gradient."))
    background_color = models.CharField(_('color'), max_length=7, default="#FFFFFF", help_text=_("The background color of the reflection gradient. Set this to match the background color of your page."))

    class Meta:
        verbose_name = _("photo effect")
        verbose_name_plural = _("photo effects")
        app_label = 'photos'

    def pre_process(self, im):
        if self.transpose_method != '':
            method = getattr(PILImage, self.transpose_method)
            im = im.transpose(method)
        if im.mode != 'RGB' and im.mode != 'RGBA':
            return im
        for name in ['Color', 'Brightness', 'Contrast', 'Sharpness']:
            factor = getattr(self, name.lower())
            if factor != 1.0:
                im = getattr(ImageEnhance, name)(im).enhance(factor)
        for name in self.filters.split('->'):
            image_filter = getattr(ImageFilter, name.upper(), None)
            if image_filter is not None:
                try:
                    im = im.filter(image_filter)
                except ValueError:
                    pass
        return im

    def post_process(self, im):
        if self.reflection_size != 0.0:
            im = add_reflection(im, bgcolor=self.background_color, amount=self.reflection_size, opacity=self.reflection_strength)
        return im


class Watermark(BaseEffect):
    image = models.ImageField(_('image'), upload_to=PHOTOS_DIR + "/watermarks")
    style = models.CharField(_('style'), max_length=5, choices=WATERMARK_STYLE_CHOICES, default='scale')
    opacity = models.FloatField(_('opacity'), default=1, help_text=_("The opacity of the overlay."))

    class Meta:
        verbose_name = _('watermark')
        verbose_name_plural = _('watermarks')
        app_label = 'photos'

    def post_process(self, im):
        try:
            content = default_storage.open(unicode(self.image)).read()
            mark = PILImage.open(StringIO(content))
        except IOError as e:
            raise e

        return apply_watermark(im, mark, self.style, self.opacity)


class PhotoSize(models.Model):
    name = models.CharField(_('name'), max_length=20, unique=True, help_text=_('Photo size name should contain only letters, numbers and underscores. Examples: "thumbnail", "display", "small", "main_page_widget".'))
    width = models.PositiveIntegerField(_('width'), default=0, help_text=_('If width is set to "0" the image will be scaled to the supplied height.'))
    height = models.PositiveIntegerField(_('height'), default=0, help_text=_('If height is set to "0" the image will be scaled to the supplied width'))
    quality = models.PositiveIntegerField(_('quality'), choices=JPEG_QUALITY_CHOICES, default=70, help_text=_('JPEG image quality.'))
    upscale = models.BooleanField(_('upscale images?'), default=False, help_text=_('If selected the image will be scaled up if necessary to fit the supplied dimensions. Cropped sizes will be upscaled regardless of this setting.'))
    crop = models.BooleanField(_('crop to fit?'), default=False, help_text=_('If selected the image will be scaled and cropped to fit the supplied dimensions.'))
    pre_cache = models.BooleanField(_('pre-cache?'), default=False, help_text=_('If selected this photo size will be pre-cached as photos are added.'))
    increment_count = models.BooleanField(_('increment view count?'), default=False, help_text=_('If selected the image\'s "view_count" will be incremented when this photo size is displayed.'))
    effect = models.ForeignKey('PhotoEffect', null=True, blank=True, related_name='photo_sizes', verbose_name=_('photo effect'))
    watermark = models.ForeignKey('Watermark', null=True, blank=True, related_name='photo_sizes', verbose_name=_('watermark image'))

    class Meta:
        ordering = ['width', 'height']
        verbose_name = _('photo size')
        verbose_name_plural = _('photo sizes')
        app_label = 'photos'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def clear_cache(self):
        for cls in ImageModel.__subclasses__():
            for obj in cls.objects.all():
                obj.remove_size(self)
                if self.pre_cache:
                    obj.create_size(self)
        PhotoSizeCache().reset()

    def save(self, *args, **kwargs):
        if self.crop is True:
            if self.width == 0 or self.height == 0:
                raise ValueError(_("PhotoSize width and/or height can not be zero if crop=True."))
        super(PhotoSize, self).save(*args, **kwargs)
        PhotoSizeCache().reset()
        self.clear_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super(PhotoSize, self).delete()

    def _get_size(self):
        return (self.width, self.height)
    def _set_size(self, value):
        self.width, self.height = value
    size = property(_get_size, _set_size)


class PhotoSizeCache(object):
    __state = {"sizes": {}}

    def __init__(self):
        self.__dict__ = self.__state

        if not len(self.sizes):
            sizes = PhotoSize.objects.all()
            for size in sizes:
                self.sizes[size.name] = size

    def reset(self):
        self.sizes = {}


class PhotoSet(OrderingBaseModel, TendenciBaseModel):
    """
    A set of photos
    """
    PUBLISH_CHOICES = (
        (1, _('Private')),
        (2, _('Public')),
    )
    guid = models.CharField(max_length=40)
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    publish_type = models.IntegerField(_('publish_type'), choices=PUBLISH_CHOICES, default=2)
    group = models.ForeignKey(Group, null=True, default=get_default_group, on_delete=models.SET_NULL)
    tags = TagField(blank=True, help_text=_("Tags are separated by commas, ex: Tag 1, Tag 2, Tag 3"))
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    class Meta:
        verbose_name = _('Photo Album')
        verbose_name_plural = _('Photo Album')
        permissions = (("view_photoset", _("Can view photoset")),)
        app_label = 'photos'

    objects = PhotoSetManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())

        super(PhotoSet, self).save()

        if not self.is_public():
            for photo in Image.objects.filter(photoset=self.pk):
                set_s3_file_permission(photo.image.file, public=False)
                cache_set = cache.get("photos_cache_set.%s" % photo.pk)
                if cache_set is not None:
                    # TODO remove cached images
                    cache.delete_many(cache.get("photos_cache_set.%s" % photo.pk))
                    cache.delete("photos_cache_set.%s" % photo.pk)

    def get_default_cover_photo_small(self):
        return settings.STATIC_URL + "images/default-photo-small.jpg"

    def get_default_cover_photo(self):
        return settings.STATIC_URL + "images/default-photo-album-cover.jpg"

    def get_cover_photo(self, *args, **kwargs):
        """ get latest thumbnail url """
        cover_photo = None

        if hasattr(self, 'cover_photo'):
            return self.cover_photo

        try:
            cover_photo = AlbumCover.objects.get(photoset=self).photo
            self.cover_photo = cover_photo
        except AlbumCover.DoesNotExist:
            try:
                cover_photo = self.image_set.latest('id')
                self.cover_photo = cover_photo
            except:
                pass

        # photo record exists; check if file exists
        if cover_photo and not cover_photo.file_exists():
            return None

        return cover_photo

    def check_perm(self, user, permission, *args, **kwargs):
        """
            has_perms(self, user, permission, *args, **kwargs)
            returns boolean
        """
        if user == self.author or user.has_perm(permission):
            return True
        return False

    @models.permalink
    def get_absolute_url(self):
        return ("photoset_details", [self.pk])

    def get_images(self, user=None, status=True, status_detail='active'):
        """
        Returns the images of this photosets and filters according
        to the given user's permissions.
        This makes use of the search index to avoid hitting the database.
        """
        # user information
        user = user or AnonymousUser()

        filters = get_query_filters(user, 'photos.view_image')

        photos = Image.objects.filter(filters).filter(photoset=self.pk)

        if user.is_authenticated():
            photos = photos.distinct()

        return photos

    def delete_all_images(self):
        images = Image.objects.filter(photoset=self.pk)

        # method deletes actual image
        for image in images:
            image.delete()

    def delete(self, *args, **kwargs):
        """
        Deleting a photo-set deletes all the images
        associated with the photo-set.
        """
        self.delete_all_images()
        super(PhotoSet, self).delete(*args, **kwargs)

    def is_public(self):
        return all([self.allow_anonymous_view,
            self.status,
            self.status_detail.lower() == "active"]
            )


class Image(OrderingBaseModel, ImageModel, TendenciBaseModel):
    """
    A photo with its details
    """
    SAFETY_LEVEL = (
        (1, _('Safe')),
        (2, _('Not Safe')),
    )
    EXIF_KEYS = ('DateTimeOriginal',
                 'DateTime',
                 'ApertureValue',
                 'GPSInfo',
                 'Make',
                 'Model',
                 'Software',
                 'ExifImageWidth',
                 'ExifImageHeight',
                 'XResolution',
                 'YResolution',
                 'ResolutionUnit',
                 'SubjectLocation',
                 )

    guid = models.CharField(max_length=40, editable=False)
    title = models.CharField(_('title'), max_length=200)
    title_slug = models.SlugField(_('slug'))
    caption = models.TextField(_('caption'), blank=True)
    date_added = models.DateTimeField(_('date added'), auto_now_add=True, editable=False)
    is_public = models.BooleanField(_('public'), default=True, help_text=_('Public photographs will be displayed in the default views.'))
    member = models.ForeignKey(User, related_name="added_photos", blank=True, null=True, on_delete=models.SET_NULL)
    safetylevel = models.IntegerField(_('safety level'), choices=SAFETY_LEVEL, default=3)
    photoset = models.ManyToManyField(PhotoSet, blank=True, verbose_name=_('photo set'))
    tags = TagField(blank=True, help_text=_("Comma delimited (eg. mickey, donald, goofy)"))
    license = models.ForeignKey('License', null=True, blank=True)
    group = models.ForeignKey(Group, null=True, default=get_default_group, on_delete=models.SET_NULL, blank=True)
    exif_data = DictField(_('exif'), null=True)
    photographer = models.CharField(_('Photographer'),
                                    blank=True, null=True,
                                    max_length=100)

    # html-meta tags
    meta = models.OneToOneField(MetaTags, blank=True, null=True)

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        methods coupled to this instance.
        """
        return PhotoMeta().get_meta(self, name)

    class Meta:
        permissions = (("view_image", "Can view image"),)
        app_label = 'photos'

    def save(self, *args, **kwargs):
        initial_save = not self.id
        if not self.id:
            self.guid = str(uuid.uuid1())

        super(Image, self).save(*args, **kwargs)
       # # clear the cache
       # caching.instance_cache_clear(self, self.pk)
       # caching.cache_clear(PHOTOS_KEYWORDS_CACHE, key=self.pk)

       # # re-add instance to the cache
       # caching.instance_cache_add(self, self.pk)

        if not self.is_public_photo() or not self.is_public_photoset():
            if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE and hasattr(self.image, 'file'):
                set_s3_file_permission(self.image.file, public=False)
            cache_set = cache.get("photos_cache_set.%s" % self.pk)
            if cache_set is not None:
                # TODO remove cached images
                cache.delete_many(cache.get("photos_cache_set.%s" % self.pk))
                cache.delete("photos_cache_set.%s" % self.pk)

        if initial_save:
            try:
                exif_exists = self.get_exif_data()
                if exif_exists:
                    self.save()
            except AttributeError:
                pass

    def delete(self, *args, **kwargs):
        """
        Delete image-file and all resized versions
        """

        super(Image, self).delete(*args, **kwargs)

        if self.image:
            cache_path = self.cache_path()

            # delete cached [resized] versions
            try:
                filename_list = default_storage.listdir(cache_path)[1]
                for filename in filename_list:
                    try:
                        default_storage.delete(os.path.join(cache_path, filename))
                    except OSError:
                        pass
            except OSError:
                pass

            # delete actual image; do not save() self.instance
            self.image.delete(save=False)



    @models.permalink
    def get_absolute_url(self):
        try:
            photo_set = self.photoset.all()[0]
        except IndexError:
            return ("photo", [self.pk])
        return ("photo", [self.pk, photo_set.pk])

    def get_exif_data(self):
        """
        Extract EXIF data from image and store in the field exif_data.
        """
        try:
            img = PILImage.open(default_storage.open(self.image.name))
            exif = img._getexif()
        except (AttributeError, IOError):
            return False

        if exif:
            for tag, value in exif.items():
                key = PILTAGS.get(tag, tag)
                if key in self.EXIF_KEYS:
                    self.exif_data[key] = value

        self.exif_data['lat'], self.exif_data['lng'] = self.get_lat_lng(
                                    self.exif_data.get('GPSInfo'))
        self.exif_data['location'] = self.get_location_via_latlng(
                                            self.exif_data['lat'],
                                            self.exif_data['lng']
                                        )
        return True

    def get_lat_lng(self, gps_info):
        """
        Calculate the latitude and longitude from gps_info.
        """
        lat, lng = None, None
        if isinstance(gps_info, dict):
            try:
                lat = [float(x)/float(y) for x, y in gps_info[2]]
                latref = gps_info[1]
                lng = [float(x)/float(y) for x, y in gps_info[4]]
                lngref = gps_info[3]
            except (KeyError, ZeroDivisionError):
                return None, None

            lat = lat[0] + lat[1]/60 + lat[2]/3600
            lng = lng[0] + lng[1]/60 + lng[2]/3600
            if latref == 'S':
                lat = -lat
            if lngref == 'W':
                lng = -lng

        return lat, lng

    def get_location_via_latlng(self, lat, lng):
        """
        Get location via lat and lng.
        """
        if lat and lng:
            url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false' % (lat, lng)
            r = requests.get(url)
            if r.status_code == 200:
                data = simplejson.loads(r.content)
                for result in data.get('results'):
                    types = result.get('types')
                    if types and types[0] == 'postal_code':
                        return result.get('formatted_address')
        return None

    def meta_keywords(self):
        return ''
#        from base.utils import generate_meta_keywords
#        keywords = caching.cache_get(PHOTOS_KEYWORDS_CACHE, key=self.pk)
#        if not keywords:
#            value = self.title + ' ' + self.caption + ' ' + self.tags
#            keywords = generate_meta_keywords(value)
#            caching.cache_add(PHOTOS_KEYWORDS_CACHE, keywords, key=self.pk)
#        return keywords

    def check_perm(self, user, permission, *args, **kwargs):
        """
            has_perms(self, user, permission, *args, **kwargs)
            returns boolean
        """
        if user == self.member or user.has_perm(permission):
            return True
        return False

    def get_next(self, set=None):
        # decide which set to pull from
        if set:
            images = Image.objects.filter(photoset=set, position__gt=self.position)
        else:
            images = Image.objects.filter(position__gt=self.position)
        images = images.values_list("position", flat=True)
        images = images.order_by('-position')
        if set:
            try:
                return Image.objects.get(photoset=set, position=min(images))
            except (ValueError, Image.MultipleObjectsReturned):
                return None
        return None

    def get_prev(self, set=None):
        # decide which set to pull from
        if set:
            images = Image.objects.filter(photoset=set, position__lt=self.position)
        else:
            images = Image.objects.filter(position__lt=self.position)
        images = images.values_list("position", flat=True)
        images = images.order_by('-position')
        if set:
            try:
                return Image.objects.get(photoset=set, position=max(images))
            except (ValueError, Image.MultipleObjectsReturned):
                return None
        return None

    def get_first(self, set=None):
        # decide which set to pull from
        if set:
            images = Image.objects.filter(photoset=set)
        else:
            return None
        images = images.values_list("position", flat=True)
        images = images.order_by('-position')
        if set:
            try:
                return Image.objects.get(photoset=set, position=min(images))
            except (ValueError, Image.MultipleObjectsReturned):
                return None
        return None

    def get_position(self, set=None):
        # decide which set to pull from
        if set:
            images = Image.objects.filter(photoset=set, position__lte=self.position)
        else:
            images = Image.objects.filter(position__lte=self.position)
        position = images.count()
        return position

    def is_public_photo(self):
        return all([self.is_public,
            self.allow_anonymous_view,
            self.status,
            self.status_detail.lower() == "active"]
            )

    def is_public_photoset(self):
        for photo_set in self.photoset.all():
            if not all([self.allow_anonymous_view,
            self.status,
            self.status_detail.lower() == "active"]
            ):
                return False
        return True

    def get_license(self):
        return self.license or self.default_license()

    def default_license(self):
        return License.objects.get(id=1)

    def file_exists(self):
        return default_storage.exists(unicode(self.image))

    def default_thumbnail(self):
        return settings.STATIC_URL + "images/default-photo-album-cover.jpg"

    def get_file_from_remote_storage(self):
        return StringIO(default_storage.open(self.image.file.name).read())

    def image_dimensions(self):
        try:
            if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                im = PILImage.open(self.get_file_from_remote_storage())
            else:
                im = PILImage.open(self.image.path)
            return im.size
        except Exception:
            return (0, 0)

    objects = PhotoManager()

    def __unicode__(self):
        return self.title

class License(models.Model):
    """
    License with details
    """
    name = models.CharField(_('name'), max_length=200)
    code = models.CharField(_('code'), max_length=200, blank=True)
    author = models.CharField(_('author'), max_length=200, blank=True)
    deed = models.URLField(_('license deed'), blank=True)
    legal_code = models.URLField(_('legal code'), blank=True)

    class Meta:
        app_label = 'photos'

    def __unicode__(self):
       return "%s" % (self.name)


class Pool(models.Model):
    """
    model for a photo to be applied to an object
    """

    photo = models.ForeignKey(Image)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    created_at = models.DateTimeField(_('created_at'), default=datetime.now)

    class Meta:
        # Enforce unique associations per object
        permissions = (("view_photopool",_("Can view photopool")),)
        unique_together = (('photo', 'content_type', 'object_id'),)
        verbose_name = _('pool')
        verbose_name_plural = _('pools')
        app_label = 'photos'

class AlbumCover(models.Model):
    """
    model to mark a photo set's album cover
    """
    photoset = models.OneToOneField(PhotoSet)
    photo = models.ForeignKey(Image)

    class Meta:
        app_label = 'photos'

    def __unicode__(self):
        return self.photo.title

# Set up the accessor methods
def add_methods(sender, instance, signal, *args, **kwargs):
    """ Adds methods to access sized images (urls, paths)

    after the Photo model's __init__ function completes,
    this method calls "add_accessor_methods" on each instance.
    """
    if hasattr(instance, 'add_accessor_methods'):
        instance.add_accessor_methods()

# connect the add_accessor_methods function to the post_init signal
post_init.connect(add_methods, sender=ImageModel)
post_init.connect(add_methods, sender=Image)
