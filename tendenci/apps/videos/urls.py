from django.conf.urls import *
from tendenci.apps.videos.feeds import LatestEntriesFeed
from tendenci.apps.site_settings.utils import get_setting

urlpath = get_setting('module', 'videos', 'url') or "videos"

urlpatterns = patterns('tendenci.apps.videos.views',
    url(r'^%s/$' % urlpath, 'search', name="video"),
    url(r'^%s/category/([^/]+)/$'  % urlpath, 'index', name="video.category"),
    url(r'^%s/search/$' % urlpath, 'search', name="video.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='video.feed'),
    url(r'^%s/([^/]+)/$' % urlpath, 'detail', name="video.details"),
)