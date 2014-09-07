from django.conf.urls import patterns, url

from tendenci.apps.social_auth.views import auth, complete, associate, associate_complete, \
                              disconnect


urlpatterns = patterns('',
    url(r'^login/(?P<backend>[^/]+)/$', auth, name='social_begin'),
    url(r'^complete/(?P<backend>[^/]+)/$', complete, name='social_complete'),
    url(r'^associate/(?P<backend>[^/]+)/$', associate, name='social_associate_begin'),
    url(r'^associate/complete/(?P<backend>[^/]+)/$', associate_complete,
        name='social_associate_complete'),
    url(r'^disconnect/(?P<backend>[^/]+)/$', disconnect, name='social_disconnect'),
)
