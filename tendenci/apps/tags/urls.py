from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.tags_list, name="tags_list"),
    re_path(r'^(?P<id>\d+)/$', views.detail, name="tag.detail"),
    re_path(r'^autocomplete/$', views.autocomplete, name="tag.autocomplete"),
]
