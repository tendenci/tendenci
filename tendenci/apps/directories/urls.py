from django.urls import path, re_path, include
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed


urlpath = get_setting('module', 'directories', 'url')
if not urlpath:
    urlpath = "directories"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="directories"),
    re_path(r'^%s/affiliates/' % urlpath, include('tendenci.apps.directories.affiliates.urls')),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="directory.search"),
    re_path(r"^%s/mylist/$" % urlpath, views.search, 
        {'my_directories_only': True}, name="directory.my_directories_only"),
    re_path(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="directory.print_view"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="directory.add"),
    re_path(r'^%s/query_price/$' % urlpath, views.query_price, name="directory.query_price"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="directory.edit"),
    re_path(r'^%s/renew/(?P<id>\d+)/$' % urlpath, views.renew, name="directory.renew"),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="directory.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="directory.delete"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='directory.feed'),
    re_path(r'^%s/logo/(?P<id>\d+)/$' % urlpath, views.logo_display, name="directory.logo"),
    re_path(r'^%s/pricing/(?P<id>\d+)/$' % urlpath, views.pricing_view, name="directory_pricing.view"),
    re_path(r'^%s/pricing/add/$' % urlpath, views.pricing_add, name="directory_pricing.add"),
    re_path(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, views.pricing_edit, name="directory_pricing.edit"),
    re_path(r'^%s/pricing/delete/(?P<id>\d+)/$' % urlpath, views.pricing_delete, name="directory_pricing.delete"),
    re_path(r'^%s/pricing/search/$' % urlpath, views.pricing_search, name="directory_pricing.search"),
    re_path(r'^%s/pending/$' % urlpath, views.pending, name="directory.pending"),
    re_path(r'^%s/approve/(?P<id>\d+)/$' % urlpath, views.approve, name="directory.approve"),
#     re_path(r'^%s/publish/(?P<id>\d+)/$' % urlpath, views.publish, name="directory.publish"),
    re_path(r'^%s/thank-you/$' % urlpath, views.thank_you, name="directory.thank_you"),

    # export directory
    re_path(r"^%s/export/$" % urlpath, views.directory_export, name="directory.export"),
    re_path(r"^%s/export/status/(?P<identifier>\d+)/$" % urlpath,
        views.directory_export_status,
        name="directory.export_status"),
    re_path(r"^%s/export/download/(?P<identifier>\d+)/$" % urlpath,
        views.directory_export_download,
        name="directory.export_download"),

    re_path(r'^%s/get_subcategories/$' % urlpath, views.get_subcategories, name="directory.get_subcategories"),


    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.details, name="directory"),
]
