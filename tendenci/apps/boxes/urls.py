from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.boxes',
    url(r'^export/$', 'views.export', name="boxes.export"),
)

