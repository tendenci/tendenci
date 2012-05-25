from django.conf.urls.defaults import patterns, url
from directories.feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'directories', 'url')
if not urlpath:
    urlpath = "directories"

urlpatterns = patterns('directories',                  
    url(r'^%s/$' % urlpath, 'views.search', name="directories"),
    url(r'^%s/search/$' % urlpath, 'views.search_redirect', name="directory.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'views.print_view', name="directory.print_view"),
    url(r'^%s/add/$' % urlpath, 'views.add', name="directory.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'views.edit', name="directory.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'views.edit_meta', name="directory.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'views.delete', name="directory.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='directory.feed'),
    url(r'^%s/pricing/(?P<id>\d+)/$' % urlpath, 'views.pricing_view', name="directory_pricing.view"),
    url(r'^%s/pricing/add/$' % urlpath, 'views.pricing_add', name="directory_pricing.add"),
    url(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, 'views.pricing_edit', name="directory_pricing.edit"),
    url(r'^%s/pricing/delete/(?P<id>\d+)/$' % urlpath, 'views.pricing_delete', name="directory_pricing.delete"),
    url(r'^%s/pricing/search/$' % urlpath, 'views.pricing_search', name="directory_pricing.search"),
    url(r'^%s/pending/$' % urlpath, 'views.pending', name="directory.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, 'views.approve', name="directory.approve"),
    url(r'^%s/thank-you/$' % urlpath, 'views.thank_you', name="directory.thank_you"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'views.details', name="directory"),
)