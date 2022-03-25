from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.search, name="navs.search"),
    re_path(r'^add/$', views.add, name="navs.add"),
    re_path(r'^detail/(?P<id>\d+)/$', views.detail, name="navs.detail"),
    re_path(r'^edit/(?P<id>\d+)/$', views.edit, name="navs.edit"),
    re_path(r'^edit/(?P<id>\d+)/items/$', views.edit_items, name="navs.edit_items"),
    re_path(r'^delete/(?P<id>\d+)/$', views.delete, name="navs.delete"),
    re_path(r'^page-select/$', views.page_select, name="navs.page_select"),
    re_path(r'^export/$', views.export, name="navs.export"),

    # for retrieving nav attributes
    re_path(r'^get-item-attrs/$', views.get_item_attrs, name="navs.get_item_attrs"),
]
