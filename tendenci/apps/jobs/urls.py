from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'jobs', 'url')
if not urlpath:
    urlpath = "jobs"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="jobs"),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="job.search"),
    url(r'^%s/my-jobs/$' % urlpath, views.my_jobs, name="myjobs"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="job.print_view"),
    url(r'^%s/add/$' % urlpath, views.add, name="job.add"),
    url(r'^%s/query_price/$' % urlpath, views.query_price, name="job.query_price"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="job.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="job.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="job.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='job.feed'),
    url(r'^%s/pricing/(?P<id>\d+)/$' % urlpath, views.pricing_view, name="job_pricing.view"),
    url(r'^%s/pricing/add/$' % urlpath, views.pricing_add, name="job_pricing.add"),
    url(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, views.pricing_edit, name="job_pricing.edit"),
    url(r'^%s/pricing/delete/(?P<id>\d+)/$' % urlpath, views.pricing_delete, name="job_pricing.delete"),
    url(r'^%s/pricing/search/$' % urlpath, views.pricing_search, name="job_pricing.search"),
    url(r'^%s/pending/$' % urlpath, views.pending, name="job.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, views.approve, name="job.approve"),
    url(r'^%s/thank-you/$' % urlpath, views.thank_you, name="job.thank_you"),
    url(r'^%s/export/$' % urlpath, views.export, name="job.export"),
    url(r'^%s/get_subcategories/$' % urlpath, views.get_subcategories, name="job.get_subcategories"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="job"),
]
