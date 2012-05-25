from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('discounts',
    url(r'^$', 'views.search', name="discounts"),
    url(r'^add/$', 'views.add', name="discount.add"),
    url(r'^detail/(?P<id>\d+)/$', 'views.detail', name="discount.detail"),
    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="discount.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="discount.delete"),
    url(r'^discounted_price/$', 'views.discounted_price', name='discount.discounted_price')
)
