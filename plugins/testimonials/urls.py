from django.conf.urls.defaults import patterns, url
from feeds import LatestEntriesFeed

urlpatterns = patterns('testimonials.views',
    url(r'^testimonials/$', 'index', name="testimonial"),
    url(r'^testimonials/search/$', 'search', name="testimonial.search"),
    url(r'^testimonials/feed/$', LatestEntriesFeed(), name='testimonial.feed'),
    url(r'^testimonials/(?P<pk>\d+)/$', 'index', name="testimonial.view"),
)