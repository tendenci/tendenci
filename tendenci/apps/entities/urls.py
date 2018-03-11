from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'entities', 'url')
if not urlpath:
    urlpath = "entities"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.index, name="entities"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, views.index, name="entity"),
    url(r'^%s/search/$' % urlpath, views.search, name="entity.search"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, views.print_view, name="entity.print_view"),
    url(r'^%s/add/$' % urlpath, views.add, name="entity.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="entity.edit"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="entity.delete"),
]
