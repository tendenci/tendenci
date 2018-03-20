from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'contributions', 'url')
if not urlpath:
    urlpath = "contributions"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.index, name="contribution"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, views.index, name="contribution"),
    url(r'^%s/search/$' % urlpath, views.search, name="contribution.search"),
]
