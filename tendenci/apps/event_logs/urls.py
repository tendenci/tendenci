from django.conf.urls import patterns, url


urlpatterns = patterns('tendenci.apps.event_logs.views',
    url(r'^$', 'index', name="event_logs"),
    url(r'^reports/summary-historical/$', 'event_summary_historical_report', name='reports-events-summary-historical'),
    url(r'^reports/summary/$', 'event_summary_report', name='reports-events-summary'),
    url(r'^reports/summary/source/([^/]+)/$', 'event_source_summary_report', name='reports-events-source'),
    url(r'^reports/summary/application/(?P<application>[^/]+)/$', 'event_application_summary_report', name='reports-events-application'),
    url(r'^(?P<id>\d+)/$', 'index', name="event_log"),
    url(r'^search/$', 'search', name="event_log.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'print_view', name="event_log.print_view"),
    url(r'^colored-image/(?P<color>\w+)/$', 'colored_image', name="event_log.colored_image"),
    url(r'^info/$', 'info', name="event_log.info"),
)
