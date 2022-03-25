from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'projects', 'url')
if not urlpath:
    urlpath = "projects"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.index, name="projects"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="projects.search"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='projects.feed'),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="projects.detail"),
]
