from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('discounts',
    url(r'^search/$', 'views.search', name="discount.search"),
    url(r'^add/$', 'views.add', name="discount.add"),
    url(r'^detail/(?P<id>\d+)/$', 'views.detail', name="discount.detail"),
    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="discount.edit"),
)
