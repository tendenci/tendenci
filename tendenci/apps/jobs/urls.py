from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'jobs', 'url')
if not urlpath:
    urlpath = "jobs"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="jobs"),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="job.search"),
    re_path(r'^%s/my-jobs/$' % urlpath, views.my_jobs, name="myjobs"),
    re_path(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="job.print_view"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="job.add"),
    re_path(r'^%s/query_price/$' % urlpath, views.query_price, name="job.query_price"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="job.edit"),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="job.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="job.delete"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='job.feed'),
    re_path(r'^%s/pricing/(?P<id>\d+)/$' % urlpath, views.pricing_view, name="job_pricing.view"),
    re_path(r'^%s/pricing/add/$' % urlpath, views.pricing_add, name="job_pricing.add"),
    re_path(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, views.pricing_edit, name="job_pricing.edit"),
    re_path(r'^%s/pricing/delete/(?P<id>\d+)/$' % urlpath, views.pricing_delete, name="job_pricing.delete"),
    re_path(r'^%s/pricing/search/$' % urlpath, views.pricing_search, name="job_pricing.search"),
    re_path(r'^%s/pending/$' % urlpath, views.pending, name="job.pending"),
    re_path(r'^%s/approve/(?P<id>\d+)/$' % urlpath, views.approve, name="job.approve"),
    re_path(r'^%s/thank-you/$' % urlpath, views.thank_you, name="job.thank_you"),
    re_path(r'^%s/export/$' % urlpath, views.export, name="job.export"),
    re_path(r'^%s/get_subcategories/$' % urlpath, views.get_subcategories, name="job.get_subcategories"),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="job"),
]
