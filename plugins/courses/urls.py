from django.conf.urls.defaults import patterns, url
from courses.feeds import LatestEntriesFeed

urlpatterns = patterns('courses.views',                  
    url(r'^courses/$', 'index', name="courses"),
    url(r'^courses/search/$', 'search', name="courses.search"),
    url(r'^courses/feed/$', LatestEntriesFeed(), name='courses.feed'),
    url(r'^courses/add/$', 'add', name="courses.add"),
    url(r'^courses/(?P<pk>[\d/]+)/$', 'detail', name="courses.detail"),
    url(r'^courses/(?P<pk>[\d/]+)/edit/$', 'edit', name="courses.edit"),
    url(r'^courses/(?P<pk>[\d/]+)/questions/$', 'edit_questions', name="courses.edit_questions"),
    url(r'^courses/(?P<pk>[\d/]+)/clone/$', 'clone', name="courses.clone"),
    url(r'^courses/(?P<pk>[\d/]+)/delete/$', 'delete', name="courses.delete"),
    url(r'^courses/(?P<pk>[\d/]+)/take/$', 'take', name="courses.take"),
    url(r'^courses/(?P<pk>[\d/]+)/completion/$', 'completion', name="courses.completion"),
    url(r'^courses/(?P<pk>[\d/]+)/add_completion/$', 'add_completion', name="courses.add_completion"),
    url(r'^courses/(?P<pk>[\d/]+)/certificate/$', 'certificate', name="courses.certificate"),
)
