from django.conf.urls.defaults import *

urlpatterns = patterns('tendenci.apps.redirects.views',
    url(r'^$', 'search', name="redirects"),
    url(r'^add/$', 'add', name="redirect.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="redirect.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="redirect.delete"),
    url(r'^export/$', 'export', name="redirect.export"),
)
