from django.conf.urls.defaults import patterns, url
from feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'case_studies', 'case_studies_url')
if not urlpath:
    urlpath = "case-studies"

urlpatterns = patterns('case_studies.views',
    url(r'^%s/$' % urlpath, 'search', name="case_study"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="case_study.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='case_study.feed'),
    url(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, 'index', name="case_study.view"),
    url(r'^%s/technology/(?P<id>\d+)/$' % urlpath, 'technology', name="case_study.technology"),
    url(r'^%s/service/(?P<id>\d+)/$' % urlpath, 'service', name="case_study.service"),
)