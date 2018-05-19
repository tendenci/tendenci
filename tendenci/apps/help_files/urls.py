from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed


urlpath = get_setting('module', 'help_files', 'url')
if not urlpath:
    urlpath = "help-files"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.index, name='help_files'),
    url(r'^%s/search/$' % urlpath, views.search, name='help_files.search'),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='help_files.feed'),
    url(r'^%s/add/$' % urlpath, views.add, name='help_files.add'),
    url(r'^%s/export/$' % urlpath, views.export, name='help_files.export'),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name='help_files.edit'),
    url(r'^%s/topic/(?P<id>\d+)/$' % urlpath, views.topic, name='help_files.topic'),
    url(r'^%s/requests/$' % urlpath, views.requests, name='help_files.requests'),
    url(r'^%s/request/$' % urlpath, views.request_new, name='help_files.request'),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name='help_file.details'),
]
