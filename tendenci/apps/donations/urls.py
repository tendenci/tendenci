from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.donations.views',
    url(r'^donations/$', 'add', name="donation.add"),
    url(r'^donations/conf/(?P<id>\d+)/$', 'add_confirm', name="donation.add_confirm"),
    url(r'^donations/(?P<id>\d+)/$', 'detail', name="donation.view"),
    url(r'^donations/receipt/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$', 'receipt', name="donation.receipt"),
    url(r'^donations/search/$', 'search', name="donation.search"),
)