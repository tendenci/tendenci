from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('categories',                  
    url(r'^update/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[\w\d]+)/$', 
        'views.update', name="category.update"),
)