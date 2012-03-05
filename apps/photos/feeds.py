from django.contrib.syndication.views import Feed

from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from photos.models import Image, PhotoSet

class LatestAlbums(SubFeed):
    title =  '%s - Latest Photo Albums' % get_setting('site','global','sitedisplayname')
    link =  "/photos/"
    description =  "Latest Photo Albums from %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = PhotoSet.objects.filter(**PUBLIC_FILTER).order_by('-update_dt')[:20]
        return items
    
    def item_title(self, item):
        return item.name

    def item_description(self, item):
        if item.get_cover_photo:
            return '<a href="%s"><img src="%s" /></a><br />%s' % (item.get_absolute_url(), item.get_cover_photo().get_medium_640_url(), item.description)
        return item.description

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class LatestAlbumPhotos(Feed):
    pass
#     def get_object(self, request, set_id):
#         return PhotoSet.objects.get(id=set_id)
# 
#     def title(self, album):
#         site_name = get_setting('site','global','sitedisplayname')
#         return '%s - Latest Album Photos "%s" ' % (site_name, album.name)
# 
#     def description(self, album):
#         site_name = get_setting('site','global','sitedisplayname')
#         return 'Latest Album [%s] Photos from %s' % (album.name, site_name)
# 
#     link =  "/photos/"
# 
#     def items(self, album):
#         return album.image_set.all()
#     
#     def item_title(self, item):
#         return item.title

class PhotoSetSitemap(TendenciSitemap):
    """ Sitemap information for photo sets """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        items = PhotoSet.objects.filter(**PUBLIC_FILTER).order_by('-update_dt')
        return items

    def lastmod(self, obj):
        return obj.update_dt


class ImageSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.3
    
    def items(self):
        items = Image.objects.filter(**PUBLIC_FILTER).order_by('-update_dt')
        return items

    def lastmod(self, obj):
        return obj.update_dt
