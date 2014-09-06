from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.core.versions',
    url(r'^(?P<ct>\d+)/(?P<object_id>\d+)/$', 'views.version_list', name="versions"),
)
