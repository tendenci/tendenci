from django.conf.urls.defaults import patterns, url
from courses.feeds import LatestEntriesFeed

urlpatterns = patterns('courses.views',                  
    url(r'^courses/$', 'index', name="courses"),
    url(r'^courses/search/$', 'search', name="courses.search"),
    url(r'^courses/feed/$', LatestEntriesFeed(), name='courses.feed'),
    url(r'^courses/(?P<pk>[\d/]+)/$', 'detail', name="courses.detail"),
)