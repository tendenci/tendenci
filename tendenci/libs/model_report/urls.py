# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.report_list, name='model_report_list'),
    re_path(r'^(?P<slug>[\w-]+)/$', views.report, name='model_report_view'),
]
