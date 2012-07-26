from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.contrib.metrics.views',
    url(r'^$', 'index', name="metrics"),
)