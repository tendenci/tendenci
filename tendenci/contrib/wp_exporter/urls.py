from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('tendenci.contrib.wp_exporter.views',
    url(r'^$', 'index', name="wp_exporter"),
)
