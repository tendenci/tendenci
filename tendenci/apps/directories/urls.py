from django.conf.urls import url, include
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed


urlpath = get_setting('module', 'directories', 'url')
if not urlpath:
    urlpath = "directories"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="directories"),
    url(r'^%s/affiliates/' % urlpath, include('tendenci.apps.directories.affiliates.urls')),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="directory.search"),
    url(r"^%s/mylist/$" % urlpath, views.search, 
        {'my_directories_only': True}, name="directory.my_directories_only"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="directory.print_view"),
    url(r'^%s/add/$' % urlpath, views.add, name="directory.add"),
    url(r'^%s/query_price/$' % urlpath, views.query_price, name="directory.query_price"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="directory.edit"),
    url(r'^%s/renew/(?P<id>\d+)/$' % urlpath, views.renew, name="directory.renew"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="directory.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="directory.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='directory.feed'),
    url(r'^%s/logo/(?P<id>\d+)/$' % urlpath, views.logo_display, name="directory.logo"),
    url(r'^%s/pricing/(?P<id>\d+)/$' % urlpath, views.pricing_view, name="directory_pricing.view"),
    url(r'^%s/pricing/add/$' % urlpath, views.pricing_add, name="directory_pricing.add"),
    url(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, views.pricing_edit, name="directory_pricing.edit"),
    url(r'^%s/pricing/delete/(?P<id>\d+)/$' % urlpath, views.pricing_delete, name="directory_pricing.delete"),
    url(r'^%s/pricing/search/$' % urlpath, views.pricing_search, name="directory_pricing.search"),
    url(r'^%s/pending/$' % urlpath, views.pending, name="directory.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, views.approve, name="directory.approve"),
#     url(r'^%s/publish/(?P<id>\d+)/$' % urlpath, views.publish, name="directory.publish"),
    url(r'^%s/thank-you/$' % urlpath, views.thank_you, name="directory.thank_you"),

    # export directory
    url(r"^%s/export/$" % urlpath, views.directory_export, name="directory.export"),
    url(r"^%s/export/status/(?P<identifier>\d+)/$" % urlpath,
        views.directory_export_status,
        name="directory.export_status"),
    url(r"^%s/export/download/(?P<identifier>\d+)/$" % urlpath,
        views.directory_export_download,
        name="directory.export_download"),

    url(r'^%s/get_subcategories/$' % urlpath, views.get_subcategories, name="directory.get_subcategories"),


    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.details, name="directory"),
]
