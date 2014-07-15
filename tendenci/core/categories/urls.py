from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.core.categories.views',
    url(r'^update/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[\w\d]+)/$',
        'edit_categories', name="category.update"),
)
