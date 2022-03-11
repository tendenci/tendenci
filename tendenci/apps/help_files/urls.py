from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed


urlpath = get_setting('module', 'help_files', 'url')
if not urlpath:
    urlpath = "help-files"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.index, name='help_files'),
    re_path(r'^%s/search/$' % urlpath, views.search, name='help_files.search'),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='help_files.feed'),
    re_path(r'^%s/add/$' % urlpath, views.add, name='help_files.add'),
    re_path(r'^%s/export/$' % urlpath, views.export, name='help_files.export'),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name='help_files.edit'),
    re_path(r'^%s/topic/(?P<id>\d+)/$' % urlpath, views.topic, name='help_files.topic'),
    re_path(r'^%s/requests/$' % urlpath, views.requests, name='help_files.requests'),
    re_path(r'^%s/request/$' % urlpath, views.request_new, name='help_files.request'),
    re_path(r'^%s/faqs/$' % urlpath, views.faqs, name='help_files.faqs'),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name='help_file.details'),
]
