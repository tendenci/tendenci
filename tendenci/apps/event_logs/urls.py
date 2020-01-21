from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name="event_logs"),
    #url(r'^reports/summary-historical/$', views.event_summary_historical_report, name='reports-events-summary-historical'),
    url(r'^reports/summary/$', views.event_summary_report, name='reports-events-summary'),
    #url(r'^reports/summary/source/([^/]+)/$', views.event_source_summary_report, name='reports-events-source'),
    url(r'^reports/summary/application/(?P<application>[^/]+)/$', views.event_application_summary_report, name='reports-events-application'),
    url(r'^(?P<id>\d+)/$', views.index, name="event_log"),
    url(r'^search/$', views.search, name="event_log.search"),
    url(r'^print-view/(?P<id>\d+)/$', views.print_view, name="event_log.print_view"),
    url(r'^colored-image/(?P<color>\w+)/$', views.colored_image, name="event_log.colored_image"),
    url(r'^info/$', views.info, name="event_log.info"),
]
