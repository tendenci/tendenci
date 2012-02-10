from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from site_settings.utils import get_setting
from help_files.models import HelpFile
from sitemaps import TendenciSitemap
from datetime import datetime

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Helpfiles' % get_setting('site','global','sitedisplayname')
    link =  "/help-files/"
    description =  "Latest Helpfiles by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        sqs = SearchQuerySet().filter(status=True, status_detail="Active", allow_anonymous_view=True).models(HelpFile).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.question

    def item_description(self, item):
        return item.answer

    def item_link(self, item):
        return item.get_absolute_url()

class HelpFileSitemap(TendenciSitemap):
    """ Sitemap information for help files """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):     
        sqs = HelpFile.objects.search(release_dt__lte=datetime.now()).order_by('-create_dt')
        return [sq.object for sq in sqs]
                                        
    def lastmod(self, obj):
        return obj.create_dt
