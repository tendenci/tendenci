from django.conf.urls import url
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    url(r'^testimonials/$', views.search, name="testimonials"),
    url(r'^testimonials/search/$', views.search_redirect, name="testimonial.search"),
    url(r'^testimonials/feed/$', LatestEntriesFeed(), name='testimonial.feed'),
    url(r'^testimonials/(?P<pk>\d+)/$', views.details, name="testimonial.view"),
]
