from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'projects', 'url')
if not urlpath:
    urlpath = "projects"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.index, name="projects"),
    re_path(r'^%s/add/$' % urlpath, views.ProjectCreate.as_view(), name="projects.add"),
    re_path(r'^%s/edit/(?P<pk>\d+)/$' % urlpath, views.ProjectUpdate.as_view(), name="projects.edit"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="projects.search"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='projects.feed'),
    re_path(r'^%s/approve/(?P<id>\d+)/$' % urlpath, views.approve, name="projects.approve"),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="projects.detail"),
]
