from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'trainings', 'url') or 'trainings'

urlpatterns = [
    path(f'{urlpath}/teaching-activities/add/', views.TeachingActivityCreateView.as_view(),
         name="trainings.add_teaching_activities"),
    path(f'{urlpath}/teaching-activities/', views.TeachingActivityListView.as_view(),
         name="trainings.teaching_activities"),
]
