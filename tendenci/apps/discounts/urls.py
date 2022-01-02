from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.search, name="discounts"),
    re_path(r'^add/$', views.add, name="discount.add"),
    re_path(r'^detail/(?P<id>\d+)/$', views.detail, name="discount.detail"),
    re_path(r'^edit/(?P<id>\d+)/$', views.edit, name="discount.edit"),
    re_path(r'^delete/(?P<id>\d+)/$', views.delete, name="discount.delete"),
    re_path(r'^discounted_price/$', views.discounted_price, name='discount.discounted_price'),
    re_path(r'^discounted_prices/$', views.discounted_prices, name='discount.discounted_prices'),
    re_path(r'^check_discount/$', views.discounted_prices, {'check':True}, name='discount.check_discount'),
    re_path(r'^export/$', views.export, name='discount.export'),
]
