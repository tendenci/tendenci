from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.metrics.views',
    url(r'^$', 'index', name="metrics"),
)