from django.urls import path, re_path
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    re_path(r'^testimonials/$', views.search, name="testimonials"),
    re_path(r'^testimonials/search/$', views.search_redirect, name="testimonial.search"),
    re_path(r'^testimonials/feed/$', LatestEntriesFeed(), name='testimonial.feed'),
    re_path(r'^testimonials/(?P<pk>\d+)/$', views.details, name="testimonial.view"),
]
