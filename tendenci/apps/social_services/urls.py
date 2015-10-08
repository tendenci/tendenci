from django.conf.urls import patterns, url

from tendenci.apps.site_settings.utils import get_setting
from tendenci.urls import urlpatterns as tendenci_urls

from .urlhelper import replace_urlpattern


urlpath = get_setting('module', 'users', 'url')
if not urlpath:
    urlpath = "profiles"


urlpatterns = patterns('tendenci.apps.social_services.views',
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/skills/$' % urlpath, 'skill_list', name="user.skills"),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/skills/edit/$' % urlpath, 'skill_list', {'edit':True}, name="user.skills_edit"),

    url(r'^social-services/relief-assessment/form/$', 'relief_form', name='social-services.form'),
    url(r'^social-services/map/$', 'relief_map', name='social-services.map'),
    url(r'^social-services/responders/$', 'responders_list', name='social-services.responders'),
    url(r'^social-services/relief-areas/$', 'relief_areas_list', name='social-services.relief_areas'),
    url(r'^social-services/relief-area/(?P<area_id>\d+)/$', 'relief_area_detail', name='social-services.relief_area'),
)

