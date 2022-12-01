from django.utils.translation import gettext_lazy as _
from django import forms

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.forms import FormControlWidgetMixin
from .models import Course, TeachingActivity


class CourseForm(TendenciBaseForm):
    class Meta:
        model = Course
        fields = (
            'name',
           'location_type',
           'school_category',
           'course_code',
           'summary',
           'description',
           'credits',
           'min_score',
           'status_detail',
           'user_perms',
           'member_perms',
           'group_perms',
           )


class TeachingActivityForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = TeachingActivity
        fields = ['activity_name',
                  'date',
                  'description']