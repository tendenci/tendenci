from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('tendenci.apps.navs.views',
    url(r'^$', 'search', name="navs.search"),
    url(r'^add/$', 'add', name="navs.add"),
    url(r'^detail/(?P<id>\d+)/$', 'detail', name="navs.detail"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="navs.edit"),
    url(r'^edit/(?P<id>\d+)/items/$', 'edit_items', name="navs.edit_items"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="navs.delete"),
    url(r'^page-select/$', 'page_select', name="navs.page_select"),
    url(r'^export/$', 'export', name="navs.export"),

    # for retrieving nav attributes
    url(r'^get-item-attrs/$', 'get_item_attrs', name="navs.get_item_attrs"),
)
