from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'contributions', 'url')
if not urlpath:
    urlpath = "contributions"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.index, name="contribution"),
    re_path(r'^%s/(?P<id>\d+)/$' % urlpath, views.index, name="contribution"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="contribution.search"),
]
