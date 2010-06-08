from django.conf.urls.defaults import *
from search.views import SearchView

urlpatterns = patterns('search.views',
    url(r'^$', SearchView(), name='haystack_search'),
)