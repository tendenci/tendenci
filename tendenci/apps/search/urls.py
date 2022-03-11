from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.SearchView(), name='haystack_search'),
    re_path(r'^open-search/$', views.open_search, name='open_search')
]
