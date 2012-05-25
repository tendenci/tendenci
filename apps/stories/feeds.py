from datetime import datetime

from django.db.models import Q

from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from stories.models import Story

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Stories' % get_setting('site','global','sitedisplayname')
    link =  "/stories/"
    description =  "Latest Stories by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Story.objects.filter(Q(expires=False) | Q(start_dt__lte=datetime.now()), Q(end_dt__gte=datetime.now())).filter(**PUBLIC_FILTER).filter(syndicate=True).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.full_story_link

class StorySitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = Story.objects.filter(Q(expires=False) | Q(start_dt__lte=datetime.now()), Q(end_dt__gte=datetime.now())).filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.update_dt

    def location(self, obj):
        return obj.full_story_link
