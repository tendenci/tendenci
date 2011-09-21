from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'wp_exporter.views.index', name="wp_exporter"),
    url(r'^download/$', 'wp_exporter.views.download', name="wp_exporter.download"),
)
