from datetime import datetime
import itertools
import feedsmanager
from haystack.query import SearchQuerySet

from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string

from tendenci.apps.site_settings.utils import get_setting


site_url = get_setting('site', 'global', 'siteurl')
site_display_name = get_setting('site', 'global', 'sitedisplayname')
site_description = get_setting('site', 'global', 'sitedescription')
if site_description == '': site_description = _('All syndicated rss feeds on %(dname)s' % {'dname':site_display_name})

max_items = settings.MAX_RSS_ITEMS
if not max_items: max_items = 100


class GlobalFeed(Feed):
    title =  _('%(dname)s RSS Feed' % {'dname':site_display_name})
    link = '%s/rss' % (site_url)
    description = site_description

    def __init__(self):
        Feed.__init__(self)
        self.all_items = []     # all items for this rss feed
        self.feed_for_item = {}   # item -> feed cache
        self.load_feeds_items() # load items

    def load_feeds_items(self):
        """ Load all feeds items """
        #print "creating new feeds_items"
        feeds = feedsmanager.get_all_feeds()
        for feed in feeds:
            feed_instance = feed()
            #print "Feed found: %s" % feed_instance.title
            item_per_feed_cnt = 0
            for item in feed_instance.items():
                #print "Item: %s" % feed_instance.item_title(item)
                self.feed_for_item[item] = feed_instance
                self.all_items.append(item)
                item_per_feed_cnt += 1
                if item_per_feed_cnt >= settings.MAX_FEED_ITEMS_PER_APP:
                    break

    def items(self):
        return self.all_items[:max_items]

    def item_title(self, item):
        feed = self.feed_for_item[item]
        if hasattr(feed, 'title_template') and not feed.title_template is None:
            # use the template instead of the method
            #print feed.title_template
            return render_to_string(feed.title_template, { 'obj' : item })
        return self.get_attr_item('title', item)

    def item_description(self, item):
        feed = self.feed_for_item[item]
        if hasattr(feed, 'description_template') and not feed.description_template is None:
            # use the template instead
            #print feed.description_template
            return render_to_string(feed.description_template, { 'obj' : item })
        return self.get_attr_item('description', item)

    def item_pubdate(self, item):
        return self.get_attr_item('pubdate', item)

    def item_link(self, item):
        return self.get_attr_item('link', item)

    def item_author_name(self, item):
        return self.get_attr_item('author_name', item)

    def get_attr_item(self, attr, item):
        """ Makes a call the corresponding item_* method on the feed object """
        if item in self.feed_for_item:
            # lookup item on our item->feed cache
            feed = self.feed_for_item[item]
            methodname = 'item_' + attr
            if hasattr(feed, methodname):
                # check to see if the feed has the method, if so
                # call it
                method = getattr(feed, methodname)
                return method.__func__(feed, item)
        return None

