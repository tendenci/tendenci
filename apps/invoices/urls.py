from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('invoices.views',                  
    url(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', 'view', name="invoice.view"),
    url(r'^search/$', 'search', name="invoice.search"),
)