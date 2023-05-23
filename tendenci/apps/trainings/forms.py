from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.admin.helpers import ActionForm

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.forms import FormControlWidgetMixin
from .models import Course, Certification, TeachingActivity, OutsideSchool, Transcript


class UpdateTranscriptActionForm(ActionForm):
    cert = forms.ChoiceField(required=False, label=_(' '),  choices=())
    
    def __init__(self, *args, **kwargs):
        super(UpdateTranscriptActionForm, self).__init__(*args, **kwargs)
        certs = Certification.objects.all().order_by('name')
            
        self.fields['cert'].choices = [(0,  '--- Select a Certification Track ---')] + [
                        (cert.id, cert.name) for cert in certs]


def get_participants_choices(user, corp_profile, include_user=True):
    query_set = User.objects.filter(id=user.id)
    if corp_profile:
        memberships = corp_profile.get_active_indiv_memberships()
        if memberships:
            user_ids = memberships.values_list('user_id', flat=True)
            if include_user:
                query_set = User.objects.filter(Q(id=user.id) | Q(id__in=user_ids))
            else:
                query_set = User.objects.filter(id__in=user_ids)
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
                  'certification_track',
                  'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(OutsideSchoolForm, self).__init__(*args, **kwargs)

        self.fields['certification_track'].required = False
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
                  'certification_track': outside_school.certification_track,
                  'description': outside_school.description,
                  'creator': self.request.user,
                  'owner': self.request.user}
        for user in users:
            outside_school_new = OutsideSchool(**kwargs,
                                               user=user)
            outside_school_new.save()


class ParticipantsForm(FormControlWidgetMixin, forms.Form):
    p = forms.MultipleChoiceField(label=_('Participants'), required=False,
                                              choices=(),
                            widget=forms.CheckboxSelectMultiple,)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.corp_profile = kwargs.pop('corp_profile')
        self.hidden = kwargs.pop('hidden', False)
        super(ParticipantsForm, self).__init__(*args, **kwargs)

        if self.hidden:
            self.fields['p'].widget = forms.MultipleHiddenInput()
        if self.corp_profile:
            participants_choices = get_participants_choices(self.request.user,
                                                            self.corp_profile,
                                                            include_user=False)
            self.fields['p'].choices = participants_choices
        else:
            del self.fields['p']


class CoursesInfoForm(FormControlWidgetMixin, forms.Form):
    l = forms.ModelMultipleChoiceField(
                                              label=_('Online Courses'),
                                              required=False,
                                              queryset=None,
                            widget=forms.CheckboxSelectMultiple,)
    s = forms.ModelMultipleChoiceField(required=False,
                                              label=_('Onsite Courses'),
                                              queryset=None,
                            widget=forms.CheckboxSelectMultiple,)
    include_outside_schools = forms.BooleanField(
                                     widget=forms.CheckboxInput(),
                                     initial=True, required=False)
    include_teaching_activities = forms.BooleanField(
                                     widget=forms.CheckboxInput(),
                                     initial=True, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.participants = kwargs.pop('participants')
        #self.hide_courses = kwargs.pop('hide_courses')
        super(CoursesInfoForm, self).__init__(*args, **kwargs)

        online_qs = Course.objects.filter(
                            location_type='online',
                            id__in=Transcript.objects.filter(
                                user__in=self.participants
                                ).values_list('course__id', flat=True))
        # if self.hide_courses:
        #     online_qs = online_qs.none()
            
        self.fields['l'].queryset = online_qs

        onsite_qs = Course.objects.filter(
                            location_type='onsite',
                            id__in=Transcript.objects.filter(
                                user__in=self.participants
                                ).values_list('course__id', flat=True))
        # if self.hide_courses:
        #     onsite_qs = onsite_qs.none()
        self.fields['s'].queryset = onsite_qs







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


