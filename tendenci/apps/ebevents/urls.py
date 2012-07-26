from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.ebevents.views',
    url(r'^ebevents/$', 'search', name="ebevent_list"),
    url(r'^ebevents/event/(?P<id>\d+)/$', 'detail', name="ebevent_display"),
    url(r'^ebevents/event/(?P<id>\d+)/ics/$', 'ical', name="ebevent_ical"),
)