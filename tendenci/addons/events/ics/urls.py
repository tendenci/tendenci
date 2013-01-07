from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.addons.events.ics',
    url(r'^(?P<ics_id>\d+)/$', 'views.status', name="ics.status"),
    url(r'^(?P<ics_id>\d+)/download/$', 'views.download', name="ics.download"),
)

