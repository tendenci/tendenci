from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from site_settings.utils import get_setting
from articles.models import Article
from sitemaps import TendenciSitemap
from datetime import datetime

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Articles' % get_setting('site','global','sitedisplayname')
    link =  "/articles/"
    description =  "Latest Articles by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(Article).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.body

    def item_link(self, item):
        return item.get_absolute_url()

class ArticleSitemap(TendenciSitemap):
    """ Sitemap information for articles """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):     
        sqs = Article.objects.search(release_dt__lte=datetime.now()).order_by('-create_dt')
        return [sq.object for sq in sqs]
                                        
    def lastmod(self, obj):
        return obj.create_dt
