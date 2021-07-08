from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'stories', 'url')
if not urlpath:
    urlpath = "stories"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="stories"),
    re_path(r'^%s/(?P<id>\d+)/$' % urlpath, views.details, name="story"),
    re_path(r'^%s/print/(?P<id>\d+)/$' % urlpath, views.print_details, name="story.print_details"),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="story.search"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="story.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="story.edit"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="story.delete"),
    re_path(r'^%s/export/$' % urlpath, views.export, name="story.export"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='story.feed'),
]
