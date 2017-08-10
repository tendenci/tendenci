from __future__ import absolute_import
from django.conf.urls import patterns, url
from .feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.testimonials.views',
    url(r'^testimonials/$', 'search', name="testimonials"),
    url(r'^testimonials/search/$', 'search_redirect', name="testimonial.search"),
    url(r'^testimonials/feed/$', LatestEntriesFeed(), name='testimonial.feed'),
    url(r'^testimonials/(?P<pk>\d+)/$', 'details', name="testimonial.view"),
)