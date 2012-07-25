from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.boxes',
    url(r'^export/$', 'views.export', name="boxes.export"),
)

