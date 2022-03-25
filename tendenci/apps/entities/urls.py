from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'entities', 'url')
if not urlpath:
    urlpath = "entities"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.index, name="entities"),
    re_path(r'^%s/(?P<id>\d+)/$' % urlpath, views.index, name="entity"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="entity.search"),
    re_path(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, views.print_view, name="entity.print_view"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="entity.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="entity.edit"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="entity.delete"),
]
