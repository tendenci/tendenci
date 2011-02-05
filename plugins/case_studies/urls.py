from django.conf.urls.defaults import patterns, url
from feeds import LatestEntriesFeed

urlpatterns = patterns('case_studies.views',
    url(r'^case-studies/$', 'index', name="case_study"),
    url(r'^case-studies/search/$', 'search', name="case_study.search"),
    url(r'^case-studies/feed/$', LatestEntriesFeed(), name='case_study.feed'),
    url(r'^case-studies/(?P<slug>[\w\-]+)/$', 'index', name="case_study.view"),
    url(r'^case-studies/category/(?P<id>\d+)/$', 'category', name="case_study.category"),
    url(r'^case-studies/service/(?P<id>\d+)/$', 'service', name="case_study.service"),
)