from django.conf.urls import patterns, url
from tendenci.apps.case_studies.feeds import LatestEntriesFeed
from tendenci.apps.site_settings.utils import get_setting

urlpath = get_setting('module', 'case_studies', 'case_studies_url')
if not urlpath:
    urlpath = "case-studies"

urlpatterns = patterns('tendenci.apps.case_studies.views',
    url(r'^%s/$' % urlpath, 'search', name="case_study"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="case_study.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='case_study.feed'),
    url(r'^%s/technology/(?P<id>\d+)/$' % urlpath, 'technology', name="case_study.technology"),
    url(r'^%s/service/(?P<id>\d+)/$' % urlpath, 'service', name="case_study.service"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, 'print_view', name="case_study.print_view"),
    url(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, 'detail', name="case_study.view"),
)