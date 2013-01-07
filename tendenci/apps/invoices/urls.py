from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('tendenci.apps.invoices.views',  
    url(r'^$',                                'search', name="invoices"),
    url(r'^export/',                          'export', name="invoice.export"),
    url(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', 'view', name="invoice.view"),
    url(r'^print/(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', 'view',
        {'template_name': 'invoices/print_view.html'}, name="invoice.print_view"),
    url(r'^adjust/(?P<id>\d+)/$',             'adjust', name="invoice.adjust"),
    url(r'^detail/(?P<id>\d+)/$',             'detail', name="invoice.detail"),
    url(r'^mark_as_paid/(?P<id>\d+)/$', 'mark_as_paid', name="invoice.mark_as_paid"),
    url(r'^void_payment/(?P<id>\d+)/$', 'void_payment', name="invoice.void_payment"),
    url(r'^search/$',                         'search', name="invoice.search"),
    # invoice reports
    url(r'^report/top_spenders/$', 'report_top_spenders', name="reports-top-spenders"),
)
