from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('tendenci.contrib.wp_importer.views',
    url(r'^$', 'index'),
    url(r'^detail/(?P<task_id>[-\w]+)/$', 'detail'),
)
