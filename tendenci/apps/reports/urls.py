from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ReportListView.as_view(), name='report_list'),
    url(r'^add/$', views.ReportCreateView.as_view(), name='report_create'),
    url(r'^(?P<pk>\d+)/$', views.ReportDetailView.as_view(), name='report_detail'),

    url(r'^(?P<report_id>\d+)/runs/add/$', views.RunCreateView.as_view(), name='report_run_create'),
    url(r'^(?P<report_id>\d+)/runs/(?P<pk>\d+)/$', views.RunDetailView.as_view(), name='report_run_detail'),
    url(r'^(?P<report_id>\d+)/runs/(?P<pk>\d+)/output/$', views.RunOutputView.as_view(), name='report_run_output'),
]
