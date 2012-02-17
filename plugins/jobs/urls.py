from django.conf.urls.defaults import patterns, url
from jobs.feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'jobs', 'jobs_url')
if not urlpath:
    urlpath = "jobs"

urlpatterns = patterns('',
    url(r'^%s/$' % urlpath, 'jobs.views.list', name="jobs"),
    url(r'^%s/search/$' % urlpath, 'jobs.views.search', name="job.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'jobs.views.print_view', name="job.print_view"),
    url(r'^%s/add/$' % urlpath, 'jobs.views.add', name="job.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'jobs.views.edit', name="job.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'jobs.views.edit_meta', name="job.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'jobs.views.delete', name="job.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='job.feed'),
    url(r'^%s/pricing/(?P<id>\d+)/$' % urlpath, 'jobs.views.pricing_view', name="job_pricing.view"),
    url(r'^%s/pricing/add/$' % urlpath, 'jobs.views.pricing_add', name="job_pricing.add"),
    url(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, 'jobs.views.pricing_edit', name="job_pricing.edit"),
    url(r'^%s/pricing/delete/(?P<id>\d+)/$' % urlpath, 'jobs.views.pricing_delete', name="job_pricing.delete"),
    url(r'^%s/pricing/search/$' % urlpath, 'jobs.views.pricing_search', name="job_pricing.search"),
    url(r'^%s/pending/$' % urlpath, 'jobs.views.pending', name="job.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, 'jobs.views.approve', name="job.approve"),
    url(r'^%s/thank-you/$' % urlpath, 'jobs.views.thank_you', name="job.thank_you"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'jobs.views.details', name="job"),
)
