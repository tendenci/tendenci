#from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
#from . import views

urlpath = get_setting('module', 'educations', 'url')
if not urlpath:
    urlpath = "educations"

urlpatterns = [
#    url(r'^%s/$' % urlpath, views.search, name="industries"),
#    url(r'^%s/(?P<id>\d+)/$' % urlpath, views.detail, name="industry"),
#    url(r'^%s/search/$' % urlpath, views.search_redirect, name="industry.search"),
#    url(r'^%s/add/$' % urlpath, views.add, name="industry.add"),
#    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="industry.edit"),
#    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="industry.delete"),
]
