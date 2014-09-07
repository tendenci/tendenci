from django.conf.urls import patterns, url
from tendenci.apps.site_settings.utils import get_setting


urlpath = get_setting('module', 'entities', 'url')
if not urlpath:
    urlpath = "entities"


urlpatterns = patterns('tendenci.apps.entities.views',
    url(r'^%s/$' % urlpath, 'index', name="entities"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, 'index', name="entity"),
    url(r'^%s/search/$' % urlpath, 'search', name="entity.search"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, 'print_view', name="entity.print_view"),
    url(r'^%s/add/$' % urlpath, 'add', name="entity.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="entity.edit"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="entity.delete"),
)
