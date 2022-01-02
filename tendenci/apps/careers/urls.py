#from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
#from . import views

urlpath = get_setting('module', 'careers', 'url')
if not urlpath:
    urlpath = "careers"

urlpatterns = [
#    re_path(r'^%s/$' % urlpath, views.search, name="industries"),
#    re_path(r'^%s/(?P<id>\d+)/$' % urlpath, views.detail, name="industry"),
#    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="industry.search"),
#    re_path(r'^%s/add/$' % urlpath, views.add, name="industry.add"),
#    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="industry.edit"),
#    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="industry.delete"),
]
