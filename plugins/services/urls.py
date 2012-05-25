from django.conf.urls.defaults import patterns, url
from services.feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'services', 'url')
if not urlpath:
    urlpath = "services"


urlpatterns = patterns('services.views',                  
    url(r'^%s/$' % urlpath, 'search', name="services"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="service.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'print_view', name="service.print_view"),
    url(r'^%s/add/$' % urlpath, 'add', name="service.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="service.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'edit_meta', name="service.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="service.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='service.feed'),
    url(r'^%s/pending/$' % urlpath, 'pending', name="service.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, 'approve', name="service.approve"),
    url(r'^%s/thank-you/$' % urlpath, 'thank_you', name="service.thank_you"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'details', name="service"),
)