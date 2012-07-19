from django.conf.urls.defaults import patterns, url
from search.views import SearchView

urlpatterns = patterns('search.views',
    url(r'^$', SearchView(), name='haystack_search'),
    url(r'^open-search/$', 'open_search', name='open_search')
)