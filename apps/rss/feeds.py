from datetime import datetime
import itertools
from haystack.query import SearchQuerySet
#from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
#from django.utils.feedgenerator import Rss201rev2Feed
from django.conf import settings
from site_settings.utils import get_setting

from articles.models import Article
from news.models import News
from pages.models import Page
from photos.models import PhotoSet
from directories.models import Directory
import feedsmanager
from django.template.loader import render_to_string

site_url = get_setting('site', 'global', 'siteurl')
site_display_name = get_setting('site', 'global', 'sitedisplayname')
site_description = get_setting('site', 'global', 'sitedescription')
if site_description == '': site_description = 'All syndicated rss feeds on %s' % site_display_name

max_items = settings.MAX_RSS_ITEMS
if not max_items: max_items = 100


class GlobalFeed(Feed):
    title =  '%s RSS Feed' % site_display_name
    link = '%s/rss' % (site_url)
    description = site_description

    def __init__(self):
        Feed.__init__(self)
        self.all_items = []     # all items for this rss feed
        self.feed_for_item = {}   # item -> feed cache
        self.load_feeds_items() # load items

    def load_feeds_items(self):
        """ Load all feeds items """
        print "creating new feeds_items"
        feeds = feedsmanager.get_all_feeds()
        for feed in feeds:
            feed_instance = feed()
            print "Feed found: %s" % feed_instance.title
            item_per_feed_cnt = 0
            for item in feed_instance.items():
                print "Item: %s" % feed_instance.item_title(item)
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
            print feed.title_template
            return render_to_string(feed.title_template, { 'obj' : item })
        return self.get_attr_item('title', item)

    def item_description(self, item):
        feed = self.feed_for_item[item]
        if hasattr(feed, 'description_template') and not feed.description_template is None:
            # use the template instead
            print feed.description_template
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

class MainRSSFeed(Feed):
    #feed_type = Rss201rev2Feed
    title =  '%s RSS Feed' % site_display_name
    link = '%s/rss' % (site_url)
    description = site_description
    #title_template = "rss/title.html"
    #description_template = "rss/description.html"

    def items(self):
        return SearchQuerySet().filter(can_syndicate=True).models(Article, News, Page, Directory,
                                                            PhotoSet).order_by('-order')[:max_items]
       

    def item_title(self, item):
        if hasattr(item.object, 'headline'):        # articles, news
            return item.object.headline         
        elif hasattr(item.object, 'title'):        # pages     
            return item.object.title
        elif hasattr(item.object, 'name'):          # photosets
            return item.object.name
        else:
            return ''
    
    def item_description(self, item):
        if hasattr(item.object, 'body'):
            return item.object.body
        elif hasattr(item.object, 'content'):
            return item.object.content
        elif hasattr(item.object, 'description'):
            return item.object.description
        else:
            return ''
    
    def item_pubdate(self, item):
        obj_name = ContentType.objects.get_for_model(item.object).name
        if obj_name  == _('article') or obj_name  == _('news'):
            return item.object.release_dt
        else:
            return item.object.update_dt
    
    def item_link(self, item):
        if not item:
            raise FeedDoesNotExist
        return '%s%s' % (site_url, item.object.get_absolute_url())
    
    def item_author_name(self, item):
        if hasattr(item.object, 'author'):
            return item.object.author.get_full_name()
        else:
            return item.object.creator.get_full_name()

    
