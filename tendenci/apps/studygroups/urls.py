from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'studygroups', 'url') or 'study-groups'

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="studygroups.search"),
    re_path(r'^%s/add/$' % urlpath, views.add, name='studygroups.add'),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name='studygroups.edit'),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="studygroups.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name='studygroups.delete'),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='studygroups.feed'),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="studygroups.detail"),
]
