from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search, name="redirects"),
    url(r'^add/$', views.add, name="redirect.add"),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name="redirect.edit"),
    url(r'^delete/(?P<id>\d+)/$', views.delete, name="redirect.delete"),
    url(r'^export/$', views.export, name="redirect.export"),
]
