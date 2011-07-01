from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('campaign_monitor',                  
    url(r'^templates/$', 'views.template_index', name="campaign_monitor.template_index"),
    url(r'^templates/(?P<slug>[\w\-\/]+)/$', 'views.template_view', name="campaign_monitor.template_view"),
    url(r'^templates/add/$', 'views.template_add', name="campaign_monitor.template_add"),
    url(r'^templates/(?P<slug>[\w\-\/]+)/edit/$', 'views.template_edit', name="campaign_monitor.template_edit"),
)
