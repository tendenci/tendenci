from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/(?P<backend>[^/]+)/$', views.auth, name='social_begin'),
    url(r'^complete/(?P<backend>[^/]+)/$', views.complete, name='social_complete'),
    url(r'^associate/(?P<backend>[^/]+)/$', views.associate, name='social_associate_begin'),
    url(r'^associate/complete/(?P<backend>[^/]+)/$', views.associate_complete,
        name='social_associate_complete'),
    url(r'^disconnect/(?P<backend>[^/]+)/$', views.disconnect, name='social_disconnect'),
]
