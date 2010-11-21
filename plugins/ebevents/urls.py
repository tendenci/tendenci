from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('ebevents.views',                  
    url(r'^ebevents/$', 'list', name="ebevent_list"),
    url(r'^ebevents/event/(?P<id>\d+)/$', 'display', name="ebevent_display"),
    url(r'^ebevents/event/(?P<id>\d+)/ics/$', 'ical', name="ebevent_ical"),
)