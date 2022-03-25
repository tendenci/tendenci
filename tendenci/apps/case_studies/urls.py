from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'case_studies', 'case_studies_url')
if not urlpath:
    urlpath = "case-studies"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="case_study"),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="case_study.search"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='case_study.feed'),
    re_path(r'^%s/technology/(?P<id>\d+)/$' % urlpath, views.technology, name="case_study.technology"),
    re_path(r'^%s/service/(?P<id>\d+)/$' % urlpath, views.service, name="case_study.service"),
    re_path(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, views.print_view, name="case_study.print_view"),
    re_path(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, views.detail, name="case_study.view"),
]
