from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^login/(?P<backend>[^/]+)/$', views.auth, name='social_begin'),
    re_path(r'^complete/(?P<backend>[^/]+)/$', views.complete, name='social_complete'),
    re_path(r'^associate/(?P<backend>[^/]+)/$', views.associate, name='social_associate_begin'),
    re_path(r'^associate/complete/(?P<backend>[^/]+)/$', views.associate_complete,
        name='social_associate_complete'),
    re_path(r'^disconnect/(?P<backend>[^/]+)/$', views.disconnect, name='social_disconnect'),
]
