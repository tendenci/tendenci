from django.conf.urls.defaults import *

urlpatterns = patterns('plugins.grantstation_link.views',
    url(r'^grantstation-link/$', 'grantstation_redirect', name="grantstation_redirect"),
    url(r'^grantstation-link/(?P<offset>\d+)/$', 'grantstation_redirect', name="grantstation_redirect_offset"),
)
