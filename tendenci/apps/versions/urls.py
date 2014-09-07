from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.versions',
    url(r'^(?P<ct>\d+)/(?P<object_id>\d+)/$', 'views.version_list', name="versions"),
)
