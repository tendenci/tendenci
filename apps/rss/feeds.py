from datetime import datetime
import itertools
from haystack.query import SearchQuerySet
from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.contrib.contenttypes.models import ContentType
from site_settings.utils import get_setting

from articles.models import Article
from news.models import News
from pages.models import Page

site_url = get_setting('site', 'global', 'siteurl')
site_display_name = get_setting('site', 'global', 'sitedisplayname')

#http://docs.djangoproject.com/en/dev/ref/contrib/syndication/
#http://docs.haystacksearch.org/dev/searchqueryset_api.html

class ALLFeed(Feed):
    title =  "All syndicated content on " + site_display_name
    link = site_url
    description = ""
    #title_template = "rss/title.html"
    #description_template = "rss/description.html"

    def items(self, obj):
        return itertools.chain(SearchQuerySet().filter(syndicate=1, status=1,  
                                       status_detail='active',
                                       release_dt__lte=datetime.now()).models(Article).order_by('-create_dt'),
                SearchQuerySet().filter(syndicate=1, status=1,  
                                       status_detail='active',
                                       release_dt__lte=datetime.now()).models(News).order_by('-create_dt'),
                SearchQuerySet().filter(syndicate=1, status=1,  
                                       status_detail='active',
                                       release_dt__lte=datetime.now()).models(Page).order_by('-create_dt'),

               )

    def item_title(self, item):
        return item.object.title
    
    def item_description(self, item):
        return item.object.description
    
    def item_pubdate(self, item):
        obj_name = ContentType.objects.get_for_model(item.object).name
        if obj_name  == _('article') or obj_name  == _('news'):
            return item.object.release_dt
        else:
            return item.object.update_dt
    
    def item_link(self, item):
        if not item:
            raise FeedDoesNotExist
        return item.get_absolute_url()