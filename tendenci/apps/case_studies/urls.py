from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'case_studies', 'case_studies_url')
if not urlpath:
    urlpath = "case-studies"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="case_study"),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="case_study.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='case_study.feed'),
    url(r'^%s/technology/(?P<id>\d+)/$' % urlpath, views.technology, name="case_study.technology"),
    url(r'^%s/service/(?P<id>\d+)/$' % urlpath, views.service, name="case_study.service"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, views.print_view, name="case_study.print_view"),
    url(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, views.detail, name="case_study.view"),
]
