from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.tags_list, name="tags_list"),
    url(r'^(?P<id>\d+)/$', views.detail, name="tag.detail"),
    url(r'^autocomplete/$', views.autocomplete, name="tag.autocomplete"),
]
