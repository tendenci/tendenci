from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'event_logs.views.index', name="event_logs"),
    url(r'^(?P<id>\d+)/$', 'event_logs.views.index', name="event_log"),
    url(r'^search/$', 'event_logs.views.search', name="event_log.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'event_logs.views.print_view', name="event_log.print_view"),
    url(r'^colored-image/(?P<color>\w+)/$', 'event_logs.views.colored_image', name="event_log.colored_image"),
    url(r'^info/$', 'event_logs.views.info', name="event_log.info"),
)
