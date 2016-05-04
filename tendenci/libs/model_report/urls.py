# -*- coding: utf-8 -*-
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import *

from tendenci.libs.model_report.views import report, report_list


urlpatterns = patterns('',
    url(r'^$', report_list, name='model_report_list'),
    url(r'^(?P<slug>[\w-]+)/$', report, name='model_report_view'),
)
