# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.report_list, name='model_report_list'),
    url(r'^(?P<slug>[\w-]+)/$', views.report, name='model_report_view'),
]
