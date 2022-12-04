from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.forms import FormControlWidgetMixin
from .models import Course, TeachingActivity, OutsideSchool


def get_participants_choices(user, corp_profile):
    query_set = User.objects.filter(id=user.id)
    if corp_profile:
        memberships = corp_profile.get_active_indiv_memberships()
        if memberships:
            user_ids = memberships.values_list('user_id', flat=True)
            query_set = User.objects.filter(Q(id=user.id) | Q(id__in=user_ids))
    query_set = query_set.order_by('first_name', 'last_name')
    return [(u.id, f'{u.first_name} {u.last_name}') for u in query_set]


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
    participants = forms.MultipleChoiceField(label=_("Participants"),
                                             required=True,
                                            choices=(),
                            widget=forms.CheckboxSelectMultiple,)
    class Meta:
        model = OutsideSchool
        fields = ['school_name',
                  'date',
                  'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(OutsideSchoolForm, self).__init__(*args, **kwargs)

        if hasattr(self.request.user, 'corp_profile'):
            corp_profile = self.request.user.corp_profile
            if corp_profile:
                participants_choices = get_participants_choices(self.request.user, corp_profile)
                self.fields['participants'].choices = participants_choices
            else:
                del self.fields['participants']
        else:
            del self.fields['participants']

    def save(self, **kwargs):
        outside_school = super(OutsideSchoolForm, self).save(commit=False)
        if 'participants' not in self.fields:
            users = [self.request.user]
        else:
            users = self.cleaned_data['participants']
            users = User.objects.filter(id__in=users)

        kwargs = {'school_name': outside_school.school_name,
                  'date': outside_school.date,
                  'description': outside_school.description,
                  'creator': self.request.user,
                  'owner': self.request.user}
        for user in users:
            outside_school_new = OutsideSchool(**kwargs,
                                               user=user)
            outside_school_new.save()


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


