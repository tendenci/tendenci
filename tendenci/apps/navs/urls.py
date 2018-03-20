from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search, name="navs.search"),
    url(r'^add/$', views.add, name="navs.add"),
    url(r'^detail/(?P<id>\d+)/$', views.detail, name="navs.detail"),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name="navs.edit"),
    url(r'^edit/(?P<id>\d+)/items/$', views.edit_items, name="navs.edit_items"),
    url(r'^delete/(?P<id>\d+)/$', views.delete, name="navs.delete"),
    url(r'^page-select/$', views.page_select, name="navs.page_select"),
    url(r'^export/$', views.export, name="navs.export"),

    # for retrieving nav attributes
    url(r'^get-item-attrs/$', views.get_item_attrs, name="navs.get_item_attrs"),
]
