from django.conf.urls.defaults import patterns, url
from jobs.feeds import LatestEntriesFeed

urlpatterns = patterns('',                  
    url(r'^$', 'jobs.views.index', name="jobs"),
    url(r'^search/$', 'jobs.views.search', name="job.search"),
    url(r'^print-view/(?P<slug>[\w\-\/]+)/$', 'jobs.views.print_view', name="job.print_view"),
    url(r'^add/$', 'jobs.views.add', name="job.add"),
    url(r'^edit/(?P<id>\d+)/$', 'jobs.views.edit', name="job.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'jobs.views.edit_meta', name="job.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'jobs.views.delete', name="job.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='job.feed'),
    url(r'^(?P<slug>[\w\-\/]+)/$', 'jobs.views.index', name="job"),
)