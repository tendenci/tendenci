from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('donations.views',                  
    url(r'^$', 'add', name="donation.add"),
    url(r'^conf/(?P<id>\d+)/$', 'add_confirm', name="donation.add_confirm"), 
    url(r'^(?P<id>\d+)/$', 'view', name="donation.view"), 
    url(r'^search/$', 'search', name="donation.search"),
)