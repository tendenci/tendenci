from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'users', 'url')
if not urlpath:
    urlpath = "profiles"

urlpatterns = [
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/skills/$' % urlpath, views.skill_list, name="user.skills"),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/skills/edit/$' % urlpath, views.skill_list, {'edit':True}, name="user.skills_edit"),

    url(r'^social-services/relief-assessment/form/$', views.relief_form, name='social-services.form'),
    url(r'^social-services/map/$', views.relief_map, name='social-services.map'),
    url(r'^social-services/responders/$', views.responders_list, name='social-services.responders'),
    url(r'^social-services/relief-areas/$', views.relief_areas_list, name='social-services.relief_areas'),
    url(r'^social-services/relief-area/(?P<area_id>\d+)/$', views.relief_area_detail, name='social-services.relief_area'),
]
