from django.conf.urls.defaults import *
from tendenci.addons.help_files.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.help_files.signals import init_signals

init_signals()

urlpath = get_setting('module', 'help_files', 'url')
if not urlpath:
    urlpath = "help-files"

urlpatterns = patterns('tendenci.addons.help_files.views',
    url(r'^%s/$' % urlpath, 'index', name='help_files'),
    url(r'^%s/search/$' % urlpath, 'search', name='help_files.search'),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='help_files.feed'),
    url(r'^%s/add/$' % urlpath, 'add', name='help_files.add'),
    url(r'^%s/export/$' % urlpath, 'export', name='help_files.export'),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name='help_files.edit'),
    url(r'^%s/topic/(?P<id>\d+)/$' % urlpath, 'topic', name='help_files.topic'),
    url(r'^%s/requests/$' % urlpath, 'requests', name='help_files.requests'),
    url(r'^%s/request/$' % urlpath, 'request_new', name='help_files.request'),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'detail', name='help_file.details'),
)
