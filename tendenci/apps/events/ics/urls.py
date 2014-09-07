from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.events.ics',
    url(r'^(?P<ics_id>\d+)/$', 'views.status', name="ics.status"),
    url(r'^(?P<ics_id>\d+)/download/$', 'views.download', name="ics.download"),
)

