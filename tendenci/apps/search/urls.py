from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.SearchView(), name='haystack_search'),
    url(r'^open-search/$', views.open_search, name='open_search')
]
