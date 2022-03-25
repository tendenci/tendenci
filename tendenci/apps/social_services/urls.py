from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'users', 'url')
if not urlpath:
    urlpath = "profiles"

urlpatterns = [
    re_path(r'^%s/(?P<username>[+-.\w\d@\s]+)/skills/$' % urlpath, views.skill_list, name="user.skills"),
    re_path(r'^%s/(?P<username>[+-.\w\d@\s]+)/skills/edit/$' % urlpath, views.skill_list, {'edit':True}, name="user.skills_edit"),

    re_path(r'^social-services/relief-assessment/form/$', views.relief_form, name='social-services.form'),
    re_path(r'^social-services/map/$', views.relief_map, name='social-services.map'),
    re_path(r'^social-services/responders/$', views.responders_list, name='social-services.responders'),
    re_path(r'^social-services/relief-areas/$', views.relief_areas_list, name='social-services.relief_areas'),
    re_path(r'^social-services/relief-area/(?P<area_id>\d+)/$', views.relief_area_detail, name='social-services.relief_area'),
]
