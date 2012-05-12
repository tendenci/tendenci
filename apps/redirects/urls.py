from django.conf.urls.defaults import *

urlpatterns = patterns('',         
    url(r'^$', 'redirects.views.search', name="redirects"),         
    url(r'^add/$', 'redirects.views.add', name="redirect.add"),
    url(r'^edit/(?P<id>\d+)/$', 'redirects.views.edit', name="redirect.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'redirects.views.delete', name="redirect.delete"),
    url(r'^export/$', 'redirects.views.export', name="redirect.export"),
)
