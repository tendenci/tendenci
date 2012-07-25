from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('tendenci.apps.wp_exporter.views',
    url(r'^$', 'index', name="wp_exporter"),
)
