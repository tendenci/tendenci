from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'videos', 'url') or "videos"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="video"),
    re_path(r'^%s/category/([^/]+)/$' % urlpath, views.index, name="video.category"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="video.search"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='video.feed'),
    re_path(r'^%s/add/$' % urlpath, views.add, name="video.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="video.edit"),
    re_path(r'^%s/([^/]+)/$' % urlpath, views.detail, name="video.details"),
]
