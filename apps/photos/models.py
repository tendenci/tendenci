import uuid


from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


from photologue.models import *
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from perms.utils import is_admin, is_member, is_developer
from photos.managers import PhotoManager, PhotoSetManager
from meta.models import Meta as MetaTags
from photos.module_meta import PhotoMeta
from haystack.query import SearchQuerySet


class PhotoSet(TendenciBaseModel):
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
    tags = TagField(blank=True, help_text="Tags are separated by commas, ex: Tag 1, Tag 2, Tag 3")
    author = models.ForeignKey(User)

    class Meta:
        verbose_name = _('photo set')
        verbose_name_plural = _('photo sets')
        permissions = (("view_photoset","Can view photoset"),)
        
    objects = PhotoSetManager()
        
    def save(self):
        if not self.id:
            self.guid = str(uuid.uuid1())
            
        super(PhotoSet, self).save()

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
        if not cover_photo.file_exists():
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

    def __unicode__(self):
        return self.name
        
    def get_images(self, user=None, status=True, status_detail='active'):
        """
        Returns the images of this photosets and filters according
        to the given user's permissions.
        This makes use of the search index to avoid hitting the database.
        """
        
        sqs = SearchQuerySet().models(Image).filter(photosets=self.pk)

        # user information
        user = user or AnonymousUser()
        
        if hasattr(user, 'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user
        
        sqs = PhotoSet.objects._permissions_sqs(sqs, user, status, status_detail)
        
        return sqs        

class Image(ImageModel, TendenciBaseModel):
    """
    A photo with its details
    """
    SAFETY_LEVEL = (
        (1, _('Safe')),
        (2, _('Not Safe')),
    )
    guid = models.CharField(max_length=40, editable=False) 
    title = models.CharField(_('title'), max_length=200)
    title_slug = models.SlugField(_('slug'))
    caption = models.TextField(_('caption'), blank=True)
    date_added = models.DateTimeField(_('date added'), auto_now_add=True, editable=False)
    is_public = models.BooleanField(_('public'), default=True, help_text=_('Public photographs will be displayed in the default views.'))
    member = models.ForeignKey(User, related_name="added_photos", blank=True, null=True)
    safetylevel = models.IntegerField(_('safety level'), choices=SAFETY_LEVEL, default=3)
    photoset = models.ManyToManyField(PhotoSet, blank=True, verbose_name=_('photo set'))
    tags = TagField(blank=True, help_text="Comma delimited (eg. mickey, donald, goofy)")
    license = models.ForeignKey('License', null=True, blank=True)
    
    # html-meta tags
    meta = models.OneToOneField(MetaTags, blank=True, null=True)
    
    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        methods coupled to this instance.
        """    
        return PhotoMeta().get_meta(self, name)
    
    class Meta:
        permissions = (("view_image","Can view image"),)

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(Image, self).save(*args, **kwargs)       
        # clear the cache
#        caching.instance_cache_clear(self, self.pk)
#        caching.cache_clear(PHOTOS_KEYWORDS_CACHE, key=self.pk)

#        # re-add instance to the cache
#        caching.instance_cache_add(self, self.pk)
   
    def delete(self, *args, **kwargs):
        super(Image, self).delete(*args, **kwargs)   
        # delete the cache
#        caching.instance_cache_del(self, self.pk)
#        caching.cache_delete(PHOTOS_KEYWORDS_CACHE)

    @models.permalink
    def get_absolute_url(self):
        try:
            photo_set = self.photoset.all()[0]
        except IndexError:
            return ("photo", [self.pk])
        return ("photo", [self.pk, photo_set.pk])

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
        if set: images = Image.objects.filter(photoset=set, id__lt=self.id)
        else: images = Image.objects.filter(id__lt=self.id)
        images = images.values_list("id", flat=True)
        images = images.order_by('-id')
        try: return Image.objects.get(id=max(images))
        except ValueError: return None

    def get_prev(self, set=None):
        # decide which set to pull from
        if set: images = Image.objects.filter(photoset=set, id__gt=self.id)
        else: images = Image.objects.filter(id__gt=self.id)
        images = images.values_list("id", flat=True)
        images = images.order_by('-id')
        try: return Image.objects.get(id=min(images))
        except ValueError: return None
        
    def get_license(self):
        if self.license:
            return self.license
        return self.default_license()
        
    def default_license(self):
        return License.objects.get(id=1)

    def file_exists(self):
        import os
        return os.path.exists(self.image.path)
        
    def default_thumbnail(self):
        return settings.STATIC_URL + "images/default-photo-album-cover.jpg"

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
    
    def __unicode__(self):
       return "%s" % (self.name)


class Pool(models.Model):
    """
    model for a photo to be applied to an object
    """

    photo = models.ForeignKey(Image)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    created_at = models.DateTimeField(_('created_at'), default=datetime.now)

    class Meta:
        # Enforce unique associations per object
        permissions = (("view_photopool","Can view photopool"),)
        unique_together = (('photo', 'content_type', 'object_id'),)
        verbose_name = _('pool')
        verbose_name_plural = _('pools')
        
class AlbumCover(models.Model):
    """
    model to mark a photo set's album cover
    """
    photoset = models.OneToOneField(PhotoSet)
    photo = models.ForeignKey(Image)
    
    def __unicode__(self):
        return self.photo.title
