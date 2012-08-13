from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.entities.views',
    url(r'^$', 'index', name="entities"),
    url(r'^(?P<id>\d+)/$', 'index', name="entity"),
    url(r'^search/$', 'search', name="entity.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'print_view', name="entity.print_view"),
    url(r'^add/$', 'add', name="entity.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="entity.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="entity.delete"),
)