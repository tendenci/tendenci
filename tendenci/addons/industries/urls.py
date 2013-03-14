from django.conf.urls.defaults import patterns, url
from tendenci.core.site_settings.utils import get_setting

urlpath = get_setting('module', 'industries', 'url')
if not urlpath:
    urlpath = "industries"

urlpatterns = patterns('tendenci.addons.industries.views',
#    url(r'^%s/$' % urlpath, 'search', name="industries"),
#    url(r'^%s/(?P<id>\d+)/$' % urlpath, 'detail', name="industry"),
#    url(r'^%s/search/$' % urlpath, 'search_redirect', name="industry.search"),
#    url(r'^%s/add/$' % urlpath, 'add', name="industry.add"),
#    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="industry.edit"),
#    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="industry.delete"),
)
