from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugin_builder.views',
    url(r'^build/(?P<id>\d+)/$', 'build', name="plugin_builder.build"),
)
