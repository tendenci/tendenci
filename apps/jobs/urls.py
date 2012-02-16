from django.conf.urls.defaults import patterns, url
from jobs.feeds import LatestEntriesFeed

urlpatterns = patterns('',
    url(r'^$', 'jobs.views.list', name="jobs"),
    url(r'^search/$', 'jobs.views.search', name="job.search"),
    url(r'^print-view/(?P<slug>[\w\-\/]+)/$', 'jobs.views.print_view', name="job.print_view"),
    url(r'^add/$', 'jobs.views.add', name="job.add"),
    url(r'^edit/(?P<id>\d+)/$', 'jobs.views.edit', name="job.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'jobs.views.edit_meta', name="job.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'jobs.views.delete', name="job.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='job.feed'),
    url(r'^pricing/(?P<id>\d+)/$', 'jobs.views.pricing_view', name="job_pricing.view"),
    url(r'^pricing/add/$', 'jobs.views.pricing_add', name="job_pricing.add"),
    url(r'^pricing/edit/(?P<id>\d+)/$', 'jobs.views.pricing_edit', name="job_pricing.edit"),
    url(r'^pricing/delete/(?P<id>\d+)/$', 'jobs.views.pricing_delete', name="job_pricing.delete"),
    url(r'^pricing/search/$', 'jobs.views.pricing_search', name="job_pricing.search"),
    url(r'^pending/$', 'jobs.views.pending', name="job.pending"),
    url(r'^approve/(?P<id>\d+)/$', 'jobs.views.approve', name="job.approve"),
    url(r'^thank-you/$', 'jobs.views.thank_you', name="job.thank_you"),
    url(r'^(?P<slug>[\w\-\/]+)/$', 'jobs.views.details', name="job"),
)
