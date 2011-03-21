from django.contrib.syndication.views import Feed
from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet
from site_settings.utils import get_setting
from photos.models import Image, PhotoSet
from sitemaps import TendenciSitemap

class LatestAlbums(SubFeed):
    title =  '%s - Latest Photo Albums' % get_setting('site','global','sitedisplayname')
    link =  "/photos/"
    description =  "Latest Photo Albums from %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(PhotoSet).order_by('-update_dt')[:20]
        return [sq.object for sq in sqs]
    
    def item_title(self, item):
        return item.name

    description_template = 'feeds/photo-latest-albums.html'

class LatestAlbumPhotos(Feed):

    def get_object(self, request, set_id):
        return PhotoSet.objects.get(id=set_id)

    def title(self, album):
        site_name = get_setting('site','global','sitedisplayname')
        return '%s - Latest Album Photos "%s" ' % (site_name, album.name)

    def description(self, album):
        site_name = get_setting('site','global','sitedisplayname')
        return 'Latest Album [%s] Photos from %s' % (album.name, site_name)

    link =  "/photos/"

    def items(self, album):
        return album.image_set.all()
    
    def item_title(self, item):
        return item.title

    description_template = 'feeds/photo-latest-album-photos.html'


class PhotoSetSitemap(TendenciSitemap):
    """ Sitemap information for photo sets """
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        sqs = PhotoSet.objects.search().order_by('-update_dt')
        return [sq.object for sq in sqs]
                                       
    def lastmod(self, obj):
        return obj.update_dt


class ImageSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.3
    
    def items(self):
        sqs = Image.objects.search().order_by('-date_added')
        return [sq.object for sq in sqs]
                                        
    def lastmod(self, obj):
        return obj.date_added

