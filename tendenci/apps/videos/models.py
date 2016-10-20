from django.db import models
from django.core.urlresolvers import reverse
from embedly import Embedly
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.object_perms import ObjectPermission
from tagging.fields import TagField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.videos.managers import VideoManager
from tendenci.apps.site_settings.utils import get_setting

client = Embedly("438be524153e11e18f884040d3dc5c07")

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        app_label = 'videos'

    def get_absolute_url(self):
        return reverse('video.category', args=[self.slug])


class VideoType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Video Types"
        app_label = 'videos'


class Video(TendenciBaseModel):
    """
    Videos plugin to add embedding based on video url. Uses embed.ly
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    category = models.ForeignKey(Category)
    video_type = models.ForeignKey(VideoType, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/videos/%y/%m', blank=True)
    video_url = models.CharField(max_length=500, help_text='Youtube, Vimeo, etc..')
    description = tinymce_models.HTMLField()
    release_dt = models.DateTimeField(_("Release Date"), null=True)
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    ordering = models.IntegerField(blank=True, null=True)

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = VideoManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.ordering is None:
            # Append
            try:
                last = model.objects.order_by('-ordering')[0]
                self.ordering = last.ordering + 1
            except IndexError:
                # First row
                self.ordering = 0

        return super(Video, self).save(*args, **kwargs)

    class Meta:
        permissions = (("view_video","Can view video"),)
        ordering = ('ordering',)
        verbose_name = get_setting('module', 'videos', 'label') or "Video"
        verbose_name_plural = get_setting('module', 'videos', 'label_plural') or "Videos"
        app_label = 'videos'


    @models.permalink
    def get_absolute_url(self):
        return ("video.details", [self.slug])

    def video_embed_url(self):
        """
        Returns a youtube embed URL
        Attempts to convert common YouTube URL patterns
        to the URL embed pattern.

        TODO: Contribute more video service embed URL's
        """
        import re

        url_pattern = r'http:\/\/www\.youtube\.com\/watch\?v=(\w+)'
        share_pattern = r'http:\/\/youtu\.be\/(\w+)'
        repl = lambda x: 'http://www.youtube.com/embed/%s' % x.group(1)

        if re.match(url_pattern, self.video_url):
            return re.sub(url_pattern, repl, self.video_url)

        if re.match(share_pattern, self.video_url):
            return re.sub(share_pattern, repl, self.video_url)

        return self.video_url

    def embed_code(self, **kwargs):
        width = kwargs.get('width') or 600
        return get_oembed_code(self.video_url, width, 400)

    def thumbnail(self):
        return get_oembed_thumbnail(self.video_url, 600, 400)


class OembedlyCache(models.Model):
    "For better performance all oembed queries are cached in this model"
    url = models.CharField(max_length=800)
    width = models.IntegerField(db_index=True)
    height = models.IntegerField(db_index=True)
    code = models.TextField()
    thumbnail = models.CharField(max_length=800)

    class Meta:
        app_label = 'videos'

    def __unicode__(self):
        return self.url

    @staticmethod
    def get_thumbnail(url, width, height):
        try:
            return OembedlyCache.objects.filter(url=url, width=width, height=height)[0].thumbnail
        except IndexError:
            try:
                result = client.oembed(url, format='json', maxwidth=width, maxheight=height)
                thumbnail = result['thumbnail_url']
                code = result['html']
            except KeyError:
                return False
            except Exception, e:
                return False
            obj = OembedlyCache(url=url, width=width, height=height, thumbnail=thumbnail, code=code)
            obj.save()
            return thumbnail

    @staticmethod
    def get_code(url, width, height):
        try:
            instance = OembedlyCache.objects.filter(url=url, width=width, height=height)[0]
            code = instance.code
            # find and replace https: with blank for embed to become protocol independent
            if 'https:' in code:
                code = code.replace('https:', '')

            if 'http:' in code:
                code = code.replace('http:', '')

            instance.code = code
            instance.save()
            return code

        except IndexError:
            try:
                result = client.oembed(url, format='json', maxwidth=width, maxheight=height)
                thumbnail = result['thumbnail_url']
                code = result['html']
                if 'https:' in code:
                    code = code.replace('https:', '')

                if 'http:' in code:
                    code = code.replace('http:', '')

            except KeyError:
                return 'Unable to embed code for <a href="%s">%s</a>' % (url, url)
            except Exception, e:
                return 'Unable to embed code for <a href="%s">%s</a><br>Error: %s' % (url, url, e)
            obj = OembedlyCache(url=url, width=width, height=height, code=code, thumbnail=thumbnail)
            obj.save()
            return code

def get_oembed_code(url, width, height):
    return OembedlyCache.get_code(url, width, height)

def get_oembed_thumbnail(url, width, height):
    return OembedlyCache.get_thumbnail(url, width, height)
