from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'entities.views.index', name="entities"),
    url(r'^(?P<id>\d+)/$', 'entities.views.index', name="entity"),
    url(r'^search/$', 'entities.views.search', name="entity.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'entities.views.print_view', name="entity.print_view"),
    url(r'^add/$', 'entities.views.add', name="entity.add"),
    url(r'^edit/(?P<id>\d+)/$', 'entities.views.edit', name="entity.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'entities.views.delete', name="entity.delete"),
)