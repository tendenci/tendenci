from django.urls import path, re_path

from tendenci.apps.site_settings.utils import get_setting

from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'products', 'url') or 'products'
urlpatterns = [
    #re_path(r'^%s/$' % urlpath, views.search, name="products"),
    #path('%s/search/' % urlpath, views.search_redirect, name="products.search"),
    #path('%s/feed/' % urlpath, LatestEntriesFeed(), name='products.feed'),
    #re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="products.detail"),
]
