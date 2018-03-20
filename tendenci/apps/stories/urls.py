from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'stories', 'url')
if not urlpath:
    urlpath = "stories"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="stories"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, views.details, name="story"),
    url(r'^%s/print/(?P<id>\d+)/$' % urlpath, views.print_details, name="story.print_details"),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="story.search"),
    url(r'^%s/add/$' % urlpath, views.add, name="story.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="story.edit"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="story.delete"),
    url(r'^%s/export/$' % urlpath, views.export, name="story.export"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='story.feed'),
]
