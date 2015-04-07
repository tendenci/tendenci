from datetime import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.stories.models import Story

class LatestEntriesFeed(SubFeed):
    title = _('%(dname)s Latest Stories' % {'dname': get_setting('site','global','sitedisplayname')})
    link =  "/stories/"
    description = _("Latest Stories by %(dname)s" % {'dname': get_setting('site','global','sitedisplayname')})

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
        return reverse("story", args=[obj.pk])
