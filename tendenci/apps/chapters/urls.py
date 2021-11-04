from django.conf.urls import url
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    url(r'^chapters/$', views.search, name="chapters.search"),
    url(r'^chapters/add/$', views.add, name='chapters.add'),
    url(r'^chapters/add/(?P<copy_from_id>\d+)/$', views.add, name='chapters.copy_from'),
    url(r'^chapters/edit/(?P<id>\d+)/$', views.edit, name='chapters.edit'),
    url(r'^chapters/edit_app_fields/(?P<id>\d+)/$', views.edit_app_fields, name='chapters.edit_app_fields'),
    url(r'^chapters/edit/meta/(?P<id>\d+)/$', views.edit_meta, name="chapters.edit.meta"),
    url(r'^chapters/delete/(?P<id>\d+)/$', views.delete, name='chapters.delete'),
    url(r'^chapters/feed/$', LatestEntriesFeed(), name='chapters.feed'),
    url(r"^chapters/get_app_fields/$", views.get_app_fields_json,
                            name="chapters.get_app_fields"),
    url(r'^chapters/(?P<slug>[\w\-\/]+)/$', views.detail, name="chapters.detail"),
]
