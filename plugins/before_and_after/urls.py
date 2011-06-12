from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('before_and_after.views',
    url(r'^before-and-after/$', 'index', name="before_and_after"),
    url(r'^before-and-after/search/$', 'search', name="before_and_after.search"),
    url(r'^before-and-after/detail/(?P<id>\d+)/$', 'detail', name="before_and_after.detail"),
    url(r'^before-and-after/subcategories/$', 'subcategories', name="before_and_after.subcategories"),
)
