from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search, name="discounts"),
    url(r'^add/$', views.add, name="discount.add"),
    url(r'^detail/(?P<id>\d+)/$', views.detail, name="discount.detail"),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name="discount.edit"),
    url(r'^delete/(?P<id>\d+)/$', views.delete, name="discount.delete"),
    url(r'^discounted_price/$', views.discounted_price, name='discount.discounted_price'),
    url(r'^discounted_prices/$', views.discounted_prices, name='discount.discounted_prices'),
    url(r'^check_discount/$', views.discounted_prices, {'check':True}, name='discount.check_discount'),
    url(r'^export/$', views.export, name='discount.export'),
]
