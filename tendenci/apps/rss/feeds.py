from . import feedsmanager

from django.contrib.syndication.views import Feed
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.decorators import strip_control_chars


site_url = get_setting('site', 'global', 'siteurl')
site_display_name = get_setting('site', 'global', 'sitedisplayname')
site_description = get_setting('site', 'global', 'sitedescription')
if site_description == '': site_description = _('All syndicated rss feeds on %(dname)s' % {'dname':site_display_name})

max_items = settings.MAX_RSS_ITEMS
if not max_items: max_items = 100


class RSSFeed(Feed):
    description = site_description

    def __init__(self):
        super().__init__()
        self.__qualname__ = self.__class__.__name__  # https://code.djangoproject.com/ticket/29296
        self.all_items = []     # all items for this rss feed
        self.app_items = {}     # app items for this rss feed
        self.feed_for_item = {}   # item -> feed cache

    def get_feed(self, obj, request):
        """
        Django Syndication does not pass URL parameters into get_feed.
        Feed.__call__ receives them in kwargs but does not pass them to
        get_feed alas. Fixes for this include:
            1. Fixing Django to pass args and kwargs into get_feed (long lead time)
            2. Overriding __call__ here to fix that (not appealing as __call__ does a few things)
            3. Overriding get_feed and sucking them out of DJango's request.

        This implements 3, judged to be the fastest, simplest solution for now. A Django fix is ideal too.
        """
        self.app = request.resolver_match.kwargs.get('app', None)

        if self.app:
            self.title =  _(f'{site_display_name}s {self.app.title()} RSS Feed')
            self.link = f'{site_url}/{self.app}/rss'
        else:
            self.title =  _(f'{site_display_name}s RSS Feed')
            self.link = f'{site_url}/rss'

        return super().get_feed(obj, request)

    def load_feeds_items(self):
        """ Load all feeds items """
        #print("creating new feeds_items")
        if self.app:
            feeds = [feedsmanager.get_app_feed(self.app)]
            if not self.app in self.app_items:
                self.app_items[self.app] = []
        else:
            feeds = feedsmanager.get_all_feeds()

        for feed in feeds:
            feed_instance = feed()
            #print("Feed found: %s" % feed_instance.title)
            item_per_feed_cnt = 0
            for item in feed_instance.items():
                #print("Item: %s" % feed_instance.item_title(item))
                self.feed_for_item[item] = feed_instance

                self.all_items.append(item)
                if self.app:
                    self.app_items[self.app].append(item)

                item_per_feed_cnt += 1
                if item_per_feed_cnt >= settings.MAX_FEED_ITEMS_PER_APP:
                    break

    def items(self):
        if (not self.app and not self.all_items) or (self.app and not self.app in self.app_items):
            # This method is moved from '__init__' to here to avoid querying db thus
            # avoid the error "column doesn't exist" on system checks when making new
            # migrations with the 'makemigrations' command and also applying the migrations
            # with  the 'migrate' commands.
            self.load_feeds_items() # load items

        return self.app_items[self.app][:max_items] if self.app else self.all_items[:max_items]

    @strip_control_chars
    def item_title(self, item):
        feed = self.feed_for_item[item]
        if hasattr(feed, 'title_template') and feed.title_template is not None:
            # use the template instead of the method
            #print(feed.title_template)
            return render_to_string(template_name=feed.title_template, context={ 'obj' : item })
        return self.get_attr_item('title', item)

    @strip_control_chars
    def item_description(self, item):
        feed = self.feed_for_item[item]
        if hasattr(feed, 'description_template') and feed.description_template is not None:
            # use the template instead
            #print(feed.description_template)
            return render_to_string(template_name=feed.description_template, context={ 'obj' : item })
        return self.get_attr_item('description', item)

    def item_pubdate(self, item):
        return self.get_attr_item('pubdate', item)

    @strip_control_chars
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
