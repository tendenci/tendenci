from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.metrics.views',
    url(r'^$', 'index', name="metrics"),
)