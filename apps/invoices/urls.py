from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('invoices.views',                  
    url(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', 'view', name="invoice.view"),
    url(r'^print/(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', 'view',
        {'template_name': 'invoices/print_view.html'}, 
        name="invoice.print_view"),
    url(r'^search/$', 'search', name="invoice.search"),
)