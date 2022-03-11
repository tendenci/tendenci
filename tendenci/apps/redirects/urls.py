from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.search, name="redirects"),
    re_path(r'^add/$', views.add, name="redirect.add"),
    re_path(r'^edit/(?P<id>\d+)/$', views.edit, name="redirect.edit"),
    re_path(r'^delete/(?P<id>\d+)/$', views.delete, name="redirect.delete"),
    re_path(r'^export/$', views.export, name="redirect.export"),
]
