import re
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.object_perms import ObjectPermission
from tagging.fields import TagField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.videos.managers import VideoManager
from tendenci.apps.site_settings.utils import get_setting
from tendenci.libs.abstracts.models import OrderingBaseModel
from .utils import get_embedly_client, ASPECT_RATIO


class Category(OrderingBaseModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        app_label = 'videos'
        ordering = ('position', 'name')

    def get_absolute_url(self):
        return reverse('video.category', args=[self.slug])


class VideoType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Video Types"
        app_label = 'videos'
        ordering = ('name',)


class Video(OrderingBaseModel, TendenciBaseModel):
    """
    Videos plugin to add embedding based on video url. Uses embed.ly
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(_('URL Path'), unique=True, max_length=200)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    video_type = models.ForeignKey(VideoType, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='uploads/videos/%y/%m', blank=True)
    video_url = models.CharField(max_length=500, help_text='Youtube, Vimeo, etc..')
    description = tinymce_models.HTMLField()
    release_dt = models.DateTimeField(_("Release Date"), null=True)
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = VideoManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.pk is None:
            # Append
            try:
                last = model.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(Video, self).save(*args, **kwargs)

    class Meta:
        #permissions = (("view_video","Can view video"),)
        ordering = ('position',)
        verbose_name = get_setting('module', 'videos', 'label') or "Video"
        verbose_name_plural = get_setting('module', 'videos', 'label_plural') or "Videos"
        app_label = 'videos'

    def get_absolute_url(self):
        return reverse('video.details', args=[self.slug])

    def video_embed_url(self):
        """
        Returns a youtube embed URL
        Attempts to convert common YouTube URL patterns
        to the URL embed pattern.

        TODO: Contribute more video service embed URL's
        """
        url_pattern = r'https:\/\/www\.youtube\.com\/watch\?v=(\w+)'
        share_pattern = r'https:\/\/youtu\.be\/(\w+)'

        def repl(x):
            return 'https://www.youtube.com/embed/%s' % x.group(1)

        if re.match(url_pattern, self.video_url):
            return re.sub(url_pattern, repl, self.video_url)

        if re.match(share_pattern, self.video_url):
            return re.sub(share_pattern, repl, self.video_url)

        return self.video_url

    def embed_code(self, **kwargs):
        width = kwargs.get('width') or 600
        height = kwargs.get('height') or 400
        return get_oembed_code(self.video_url, width, height)

    def thumbnail(self):
        return get_oembed_thumbnail(self.video_url, 600, 400)

    def is_youtube_video(self):
        return 'www.youtube.com' in self.video_url

    def youtube_video_id(self):
        if self.is_youtube_video():
            return get_embed_ready_url(self.video_url).replace('https://www.youtube.com/embed/', '')
        return None


class OembedlyCache(models.Model):
    "For better performance all oembed queries are cached in this model"
    url = models.CharField(max_length=800)
    width = models.IntegerField(db_index=True)
    height = models.IntegerField(db_index=True)
    code = models.TextField()
    thumbnail = models.CharField(max_length=800)

    class Meta:
        app_label = 'videos'

    def __str__(self):
        return self.url

    @staticmethod
    def get_thumbnail(url, width, height):
        try:
            return OembedlyCache.objects.filter(url=url, width=width, height=height)[0].thumbnail
        except IndexError:
            try:
                client = get_embedly_client()
                result = client.oembed(url, format='json', maxwidth=width, maxheight=height)
                thumbnail = result['thumbnail_url']
                code = result['html']
            except KeyError:
                return False
            except Exception:
                return False
            obj = OembedlyCache(url=url, width=width, height=height, thumbnail=thumbnail, code=code)
            obj.save()
            return thumbnail

    @staticmethod
    def get_code(url, width, height):
        if url.find('youtu') != -1:
            return '<iframe width="{width}" height="{height}" src="{url}?rel=0" allowfullscreen></iframe>'.format(
                            width=width,
                            height=height,
                            url=get_embed_ready_url(url))
        else:
        
            try:
                instance = OembedlyCache.objects.filter(url=url, width=width, height=height)[0]
                code = instance.code
                # replace http: with https:
                if 'http:' in code:
                    code = code.replace('http:', 'https:')
                code = code.replace('src="//cdn.embedly.com', 'src="https://cdn.embedly.com')
    
                instance.code = code
                instance.save()
            except IndexError:
                try:
                    client = get_embedly_client()
                    result = client.oembed(url, format='json', maxwidth=width, maxheight=height)
                    thumbnail = result['thumbnail_url']
                    code = result['html']
    
                    if 'http:' in code:
                        code = code.replace('http:', 'https:')
                    code = code.replace('src="//cdn.embedly.com', 'src="https://cdn.embedly.com')
                except KeyError:
                    # Embedly is not available - try the alternative way
                    width, height = int(width), int(height)
                    if width < height:
                        # adjust the height
                        height = int(round(width/ASPECT_RATIO))
                    return '<iframe width="{width}" height="{height}" src="{url}" allowfullscreen></iframe>'.format(
                            width=width,
                            height=height,
                            url=get_embed_ready_url(url))
                    #return 'Unable to embed code for <a href="%s">%s</a>' % (url, url)
                except Exception as e:
                    return 'Unable to embed code for <a href="%s">%s</a><br>Error: %s' % (url, url, e)
                obj = OembedlyCache(url=url, width=width, height=height, code=code, thumbnail=thumbnail)
                obj.save()
    
            # Strip the obsolete attributes from iframe to avoid html validation errors
            code = code.replace('scrolling="no" ', '')
            code = code.replace('frameborder="0" ', '')
    
            return code

def get_embed_ready_url(url):
    """
    Gets the embed ready url - only for youtube and vimeo for now.
    """
    # check if it is a youtube video
    p = re.compile(r'youtube\.com/watch\?v\=([^\&\?\/]+)')
    match = p.search(url)
    if not match:
        p = re.compile(r'youtu\.be/([^\&\?\/]+)')
        match = p.search(url)
    if match:
        return 'https://www.youtube.com/embed/{}'.format(match.group(1))

    # check if it's a vimeo video
    p = re.compile(r'vimeo\.com/(\d+)')
    match = p.search(url)
    if match:
        return 'https://player.vimeo.com/video/{}'.format(match.group(1))
    return url


def get_oembed_code(url, width, height):
    return OembedlyCache.get_code(url, width, height)

def get_oembed_thumbnail(url, width, height):
    return OembedlyCache.get_thumbnail(url, width, height)
