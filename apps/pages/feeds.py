from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet
from site_settings.utils import get_setting
from pages.models import Page
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Pages' % get_setting('site','global','sitedisplayname')
    link =  "/pages/"
    description =  "Latest Pages by %s" % get_setting('site','global','sitedisplayname')

    title_template = 'feeds/page_title.html'
    description_template = 'feeds/page_description.html'

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(Page).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content
        
    def item_link(self, item):
        return item.get_absolute_url()

class PageSitemap(TendenciSitemap):
    """ Sitemap information for pages """
    changefreq = "yearly"
    priority = 0.6
    
    def items(self):
        sqs = Page.objects.search().order_by('-update_dt')
        return [sq.object for sq in sqs]
    
    def lastmod(self, obj):
        return obj.update_dt