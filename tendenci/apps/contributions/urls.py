from django.conf.urls.defaults import patterns, url
from tendenci.core.site_settings.utils import get_setting


urlpath = get_setting('module', 'contributions', 'url')
if not urlpath:
    urlpath = "contributions"


urlpatterns = patterns('tendenci.apps.contributions.views',
    url(r'^%s/$' % urlpath, 'index', name="contribution"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, 'index', name="contribution"),
    url(r'^%s/search/$' % urlpath, 'search', name="contribution.search"),
)
