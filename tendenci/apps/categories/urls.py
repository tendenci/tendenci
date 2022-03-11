from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^update/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[\w\d]+)/$',
        views.edit_categories, name="category.update"),
]
