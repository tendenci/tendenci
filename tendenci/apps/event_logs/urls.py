from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name="event_logs"),
    #re_path(r'^reports/summary-historical/$', views.event_summary_historical_report, name='reports-events-summary-historical'),
    re_path(r'^reports/summary/$', views.event_summary_report, name='reports-events-summary'),
    #re_path(r'^reports/summary/source/([^/]+)/$', views.event_source_summary_report, name='reports-events-source'),
    re_path(r'^reports/summary/application/(?P<application>[^/]+)/$', views.event_application_summary_report, name='reports-events-application'),
    re_path(r'^(?P<id>\d+)/$', views.index, name="event_log"),
    re_path(r'^search/$', views.search, name="event_log.search"),
    re_path(r'^print-view/(?P<id>\d+)/$', views.print_view, name="event_log.print_view"),
    re_path(r'^colored-image/(?P<color>\w+)/$', views.colored_image, name="event_log.colored_image"),
    re_path(r'^info/$', views.info, name="event_log.info"),
]
