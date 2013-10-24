from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.discounts.views',
    url(r'^$', 'search', name="discounts"),
    url(r'^add/$', 'add', name="discount.add"),
    url(r'^detail/(?P<id>\d+)/$', 'detail', name="discount.detail"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="discount.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="discount.delete"),
    url(r'^discounted_price/$', 'discounted_price', name='discount.discounted_price'),
    url(r'^discounted_prices/$', 'discounted_prices', name='discount.discounted_prices'),
    url(r'^check_discount/$', 'discounted_prices', {'check':True}, name='discount.check_discount'),
    url(r'^export/$', 'export', name='discount.export'),
)
