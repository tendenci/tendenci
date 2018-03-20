from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^update/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[\w\d]+)/$',
        views.edit_categories, name="category.update"),
]
