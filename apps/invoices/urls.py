from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',                  
    url(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', 'invoices.views.view', name="invoices.view"),
)