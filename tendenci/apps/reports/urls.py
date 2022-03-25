from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.ReportListView.as_view(), name='report_list'),
    re_path(r'^add/$', views.ReportCreateView.as_view(), name='report_create'),
    re_path(r'^(?P<pk>\d+)/$', views.ReportDetailView.as_view(), name='report_detail'),

    re_path(r'^(?P<report_id>\d+)/runs/add/$', views.RunCreateView.as_view(), name='report_run_create'),
    re_path(r'^(?P<report_id>\d+)/runs/(?P<pk>\d+)/$', views.RunDetailView.as_view(), name='report_run_detail'),
    re_path(r'^(?P<report_id>\d+)/runs/(?P<pk>\d+)/output/$', views.RunOutputView.as_view(), name='report_run_output'),
]
