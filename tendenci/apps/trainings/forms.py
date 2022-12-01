from django.utils.translation import gettext_lazy as _
from django import forms

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.forms import FormControlWidgetMixin
from .models import Course, TeachingActivity, OutsideSchool


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


class OutsideSchoolForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = OutsideSchool
        fields = ['school_name',
                  'date',
                  'description']


# class OutsideSchoolAdminForm(forms.ModelForm):
#     class Meta:
#         model = OutsideSchool
#         fields = ['user',
#                 'school_name',
#                 'school_category',
#                 'date',
#                 'credits',
#                 'status_detail',
#                 'description',]
#
#     def __init__(self, *args, **kwargs):
#         super(OutsideSchoolAdminForm, self).__init__(*args, **kwargs)
#         self.fields['school_category'].required = False


