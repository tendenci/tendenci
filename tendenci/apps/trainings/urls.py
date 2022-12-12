from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'trainings', 'url') or 'trainings'

urlpatterns = [
    path(f'{urlpath}/teaching-activities/add/', views.TeachingActivityCreateView.as_view(),
         name="trainings.add_teaching_activities"),
    path(f'{urlpath}/teaching-activities/', views.TeachingActivityListView.as_view(),
         name="trainings.teaching_activities"),
    path(f'{urlpath}/outside-schools/add/', views.OutsideSchoolCreateView.as_view(),
         name="trainings.add_outside_schools"),
    path(f'{urlpath}/outside-schools/', views.OutsideSchoolListView.as_view(),
         name="trainings.outside_schools"),
    path(f'{urlpath}/transcripts/', views.transcripts,
         name="trainings.transcripts"),
    re_path(fr'^{urlpath}/transcripts/c/(?P<corp_profile_id>\d+)/$', views.transcripts,
         name="trainings.transcripts_corp"),
    re_path(fr'^{urlpath}/transcripts/u/(?P<user_id>\d+)/$', views.transcripts,
         name="trainings.transcripts_user"),
]
