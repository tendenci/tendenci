from django.conf.urls.defaults import patterns, url
from resumes.feeds import LatestEntriesFeed

urlpatterns = patterns('',                  
    url(r'^$', 'resumes.views.index', name="resumes"),
    url(r'^search/$', 'resumes.views.search', name="resume.search"),
    url(r'^print-view/(?P<slug>[\w\-\/]+)/$', 'resumes.views.print_view', name="resume.print_view"),
    url(r'^add/$', 'resumes.views.add', name="resume.add"),
    url(r'^edit/(?P<id>\d+)/$', 'resumes.views.edit', name="resume.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'resumes.views.edit_meta', name="resume.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'resumes.views.delete', name="resume.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='resume.feed'),
    url(r'^(?P<slug>[\w\-\/]+)/$', 'resumes.views.index', name="resume"),
)