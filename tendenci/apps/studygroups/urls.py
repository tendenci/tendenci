from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'studygroups', 'url') or 'study-groups'

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="studygroups.search"),
    url(r'^%s/add/$' % urlpath, views.add, name='studygroups.add'),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name='studygroups.edit'),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="studygroups.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name='studygroups.delete'),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='studygroups.feed'),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="studygroups.detail"),
]
