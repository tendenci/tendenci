from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.categories.views',
    url(r'^update/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[\w\d]+)/$',
        'edit_categories', name="category.update"),
)
