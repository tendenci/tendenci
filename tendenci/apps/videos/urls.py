from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'videos', 'url') or "videos"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="video"),
    url(r'^%s/category/([^/]+)/$' % urlpath, views.index, name="video.category"),
    url(r'^%s/search/$' % urlpath, views.search, name="video.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='video.feed'),
    url(r'^%s/([^/]+)/$' % urlpath, views.detail, name="video.details"),
]
