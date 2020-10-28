from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpatterns = [
    url(r'^request/(?P<to_directory_id>\d+)/$',
        views.request_associate, name="affiliates.request_associate"),
#     url(r'^%s/requests-list/(?P<directory_id>\d+)/$' % urlpath,
#         views.requests_list, name="affiliates.requests_list"),
]