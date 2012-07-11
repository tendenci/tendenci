from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'event_logs.views.index', name="event_logs"),
    url(r'^reports/summary-historical/$', 'event_logs.views.event_summary_historical_report', name='reports-events-summary-historical'),
    url(r'^reports/summary/$', 'event_logs.views.event_summary_report', name='reports-events-summary'),
    url(r'^reports/summary/source/([^/]+)/$', 'event_logs.views.event_source_summary_report', name='reports-events-source'),
    url(r'^reports/summary/application/(?P<application>[^/]+)/$', 'event_logs.views.event_application_summary_report', name='reports-events-application'),
    url(r'^(?P<id>\d+)/$', 'event_logs.views.index', name="event_log"),
    url(r'^search/$', 'event_logs.views.search', name="event_log.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'event_logs.views.print_view', name="event_log.print_view"),
    url(r'^colored-image/(?P<color>\w+)/$', 'event_logs.views.colored_image', name="event_log.colored_image"),
    url(r'^info/$', 'event_logs.views.info', name="event_log.info"),
)
