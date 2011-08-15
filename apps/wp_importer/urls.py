from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'wp_importer.views.index'),
    url(r'^detail/$', 'wp_importer.views.detail'),
)