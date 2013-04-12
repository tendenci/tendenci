from django.conf.urls.defaults import patterns, url
from tendenci.addons.jobs.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.jobs.signals import init_signals

init_signals()

urlpath = get_setting('module', 'jobs', 'url')
if not urlpath:
    urlpath = "jobs"

urlpatterns = patterns('tendenci.addons.jobs.views',
    url(r'^%s/$' % urlpath, 'search', name="jobs"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="job.search"),
    url(r'^%s/my-jobs/$' % urlpath, 'my_jobs', name="myjobs"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'print_view', name="job.print_view"),
    url(r'^%s/add/$' % urlpath, 'add', name="job.add"),
    url(r'^%s/query_price/$' % urlpath, 'query_price', name="job.query_price"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="job.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'edit_meta', name="job.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="job.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='job.feed'),
    url(r'^%s/pricing/(?P<id>\d+)/$' % urlpath, 'pricing_view', name="job_pricing.view"),
    url(r'^%s/pricing/add/$' % urlpath, 'pricing_add', name="job_pricing.add"),
    url(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, 'pricing_edit', name="job_pricing.edit"),
    url(r'^%s/pricing/delete/(?P<id>\d+)/$' % urlpath, 'pricing_delete', name="job_pricing.delete"),
    url(r'^%s/pricing/search/$' % urlpath, 'pricing_search', name="job_pricing.search"),
    url(r'^%s/pending/$' % urlpath, 'pending', name="job.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, 'approve', name="job.approve"),
    url(r'^%s/thank-you/$' % urlpath, 'thank_you', name="job.thank_you"),
    url(r'^%s/export/$' % urlpath, 'export', name="job.export"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'detail', name="job"),
)
