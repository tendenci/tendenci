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

site_url = get_setting('site', 'global', 'siteurl')
site_display_name = get_setting('site', 'global', 'sitedisplayname')
site_description = get_setting('site', 'global', 'sitedescription')
if site_description == '': site_description = 'All syndicated rss feeds on %s' % site_display_name

max_items = settings.MAX_RSS_ITEMS_PER_OBJECT
if not max_items: max_items = 20
    

class MainRSSFeed(Feed):
    #feed_type = Rss201rev2Feed
    title =  '%s RSS Feed' % site_display_name
    link = '%s/rss' % (site_url)
    description = site_description
    #title_template = "rss/title.html"
    #description_template = "rss/description.html"

    def items(self):
        return itertools.chain(SearchQuerySet().filter(syndicate=1, status=1,  
                                       status_detail='active',
                                       allow_anonymous_view=1,
                                       release_dt__lte=datetime.now()).models(Article).order_by('-create_dt')[:max_items],
                SearchQuerySet().filter(syndicate=1, status=1,  
                                       status_detail='active',
                                       allow_anonymous_view=1,
                                       release_dt__lte=datetime.now()).models(News).order_by('-create_dt')[:max_items],
                SearchQuerySet().filter(syndicate=1, status=1,  
                                       status_detail='active',
                                       allow_anonymous_view=1).models(Page).order_by('-create_dt')[:max_items],
                SearchQuerySet().filter(status=1,  
                                       status_detail='active',
                                       allow_anonymous_view=1).models(PhotoSet).order_by('-create_dt')[:max_items],

               )

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
            return item.object.author.get_full_name
        else:
            return item.object.creator.get_full_name

    