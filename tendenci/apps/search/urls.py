from django.conf.urls.defaults import patterns, url

from tendenci.apps.search.views import SearchView

urlpatterns = patterns('tendenci.apps.search.views',
    url(r'^$', SearchView(), name='haystack_search'),
    url(r'^open-search/$', 'open_search', name='open_search')
)