from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('form_builder',                  
    url(r'^$', 'views.index', name="form"),
    url(r'^confirmation/$', 'views.confirmation', name="form.confirmation"),
)