from django.conf.urls.defaults import patterns, url
from tendenci.addons.directories.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.directories.signals import init_signals

init_signals()

urlpath = get_setting('module', 'directories', 'url')
if not urlpath:
    urlpath = "directories"

urlpatterns = patterns('tendenci.addons.directories.views',
    url(r'^%s/$' % urlpath, 'search', name="directories"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="directory.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'print_view', name="directory.print_view"),
    url(r'^%s/add/$' % urlpath, 'add', name="directory.add"),
    url(r'^%s/query_price/$' % urlpath, 'query_price', name="directory.query_price"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="directory.edit"),
    url(r'^%s/renew/(?P<id>\d+)/$' % urlpath, 'renew', name="directory.renew"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'edit_meta', name="directory.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="directory.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='directory.feed'),
    url(r'^%s/logo/(?P<id>\d+)/$' % urlpath, 'logo_display', name="directory.logo"),
    url(r'^%s/pricing/(?P<id>\d+)/$' % urlpath, 'pricing_view', name="directory_pricing.view"),
    url(r'^%s/pricing/add/$' % urlpath, 'pricing_add', name="directory_pricing.add"),
    url(r'^%s/pricing/edit/(?P<id>\d+)/$' % urlpath, 'pricing_edit', name="directory_pricing.edit"),
    url(r'^%s/pricing/delete/(?P<id>\d+)/$' % urlpath, 'pricing_delete', name="directory_pricing.delete"),
    url(r'^%s/pricing/search/$' % urlpath, 'pricing_search', name="directory_pricing.search"),
    url(r'^%s/pending/$' % urlpath, 'pending', name="directory.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, 'approve', name="directory.approve"),
    url(r'^%s/thank-you/$' % urlpath, 'thank_you', name="directory.thank_you"),

    # export directory
    url(r"^%s/export/$" % urlpath, "directory_export", name="directory.export"),
    url(r"^%s/export/status/(?P<identifier>\d+)/$" % urlpath,
        "directory_export_status",
        name="directory.export_status"),
    url(r"^%s/export/download/(?P<identifier>\d+)/$" % urlpath,
        "directory_export_download",
        name="directory.export_download"),

    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'details', name="directory"),
)
