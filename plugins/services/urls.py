from django.conf.urls.defaults import patterns, url
from services.feeds import LatestEntriesFeed

urlpatterns = patterns('services.views',                  
    url(r'^services/$', 'index', name="services"),
    url(r'^services/search/$', 'search', name="service.search"),
    url(r'^services/print-view/(?P<slug>[\w\-\/]+)/$', 'print_view', name="service.print_view"),
    url(r'^services/add/$', 'add', name="service.add"),
    url(r'^services/edit/(?P<id>\d+)/$', 'edit', name="service.edit"),
    url(r'^services/edit/meta/(?P<id>\d+)/$', 'edit_meta', name="service.edit.meta"),
    url(r'^services/delete/(?P<id>\d+)/$', 'delete', name="service.delete"),
    url(r'^services/feed/$', LatestEntriesFeed(), name='service.feed'),
    url(r'^services/pending/$', 'pending', name="service.pending"),
    url(r'^services/approve/(?P<id>\d+)/$', 'approve', name="service.approve"),
    url(r'^services/thank-you/$', 'thank_you', name="service.thank_you"),
    url(r'^services/(?P<slug>[\w\-\/]+)/$', 'index', name="service"),
)