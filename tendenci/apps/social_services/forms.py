import datetime

from django import forms
from django.forms.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _
from form_utils.forms import BetterModelForm
from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.profiles.models import Profile
from tendenci.apps.base.fields import EmailVerificationField

from tendenci.apps.social_services.models import SkillSet, ReliefAssessment, ETHNICITY_CHOICES


THIS_YEAR = datetime.date.today().year


class AddressForm(BetterModelForm):
    address = forms.CharField(label=_("Address"), max_length=150)
    address2 = forms.CharField(label=_("Address2"), max_length=100, required=False)
    city = forms.CharField(label=_("City"), max_length=50)
    state = forms.CharField(label=_("State"), max_length=50)
    zipcode = forms.CharField(label=_("Zipcode"), max_length=50)
    country = forms.CharField(label=_("Country"), max_length=50)

    class Meta:
        model = Profile
        fields = ('address',
                  'address2',
                  'city',
                  'state',
                  'zipcode',
                  'country')


class SkillSetForm(BetterModelForm):
    class Meta:
        model = SkillSet
        exclude = ('user',)

        fieldsets = [
            ('Emergency Response Skills', {
                'fields': ['paramedic',
                           'fireman',
                           'first_aid',
                           'safety_manager',
                           'police',
                           'search_and_rescue',
                           'scuba_certified',
                           'crowd_control',
                          ],}),
            ('Transportation Skills', {
                'fields': ['truck',
                           'pilot',
                           'aircraft',
                           'ship',
                           'sailor',
                          ],}),
            ('Medical Skills', {
                'fields': ['doctor',
                           'nurse',
                           'medical_specialty',
                          ],}),
            ('Communication Skills', {
                'fields': ['crisis_communication',
                           'media',
                           'author',
                           'public_speaker',
                           'politician',
                           'blogger',
                           'photographer',
                           'videographer',
                           'radio_operator',
                           'call_sign',
                           'actor',
                           'thought_leader',
                           'influencer',
                           'languages',
                          ],}),
            ('Education Skills', {
                'fields': ['teacher',
                           'school_admin',
                          ],}),
            ('Military Skills', {
                'fields': ['military_rank',
                           'military_training',
                           'desert_trained',
                           'cold_trained',
                           'marksman',
                           'security_clearance',
                          ],}),
        ]

    def __init__(self, *args, **kwargs):
        if 'edit' in kwargs:
            edit = kwargs.pop('edit', False)
        else:
            edit = False
        super(SkillSetForm, self).__init__(*args, **kwargs)
        if not edit:
            for name, field in self.fields.items():
                field.widget.attrs['disabled'] = True


class ReliefAssessmentForm(BetterModelForm):
    first_name = forms.CharField(label=_("First Name"), max_length=100,
                                 error_messages={'required': 'First Name is a required field.'})
    last_name = forms.CharField(label=_("Last Name"), max_length=100,
                                error_messages={'required': 'Last Name is a required field.'})
    initials = forms.CharField(label=_("Initial"), max_length=100, required=False)

    phone = forms.CharField(label=_("Contact Phone"), max_length=50)
    phone2 = forms.CharField(label=_("Alternate Phone"), max_length=50, required=False)

    email = EmailVerificationField(label=_("Email"),
                                error_messages={'required': 'Email is a required field.'})
    email2 = EmailVerificationField(label=_("Alternate Email"), required=False)

    dob = forms.DateField(label=_("Date of Birth"), required=False,
                          widget=SelectDateWidget(None, list(range(THIS_YEAR-100, THIS_YEAR))))
    company = forms.CharField(label=_("Company"), max_length=100, required=False)
    position_title = forms.CharField(label=_("Position Title"), max_length=50, required=False)
    education = forms.CharField(label=_("Education Level"), max_length=100, required=False)

    ethnicity = forms.ChoiceField(label="", required=False,
                                  choices=ETHNICITY_CHOICES,
                                  widget=forms.widgets.RadioSelect)

    case_notes = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':ReliefAssessment._meta.app_label,
        'storme_model':ReliefAssessment._meta.model_name.lower()}))

    items_provided = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':ReliefAssessment._meta.app_label,
        'storme_model':ReliefAssessment._meta.model_name.lower()}))

    class Meta:
        model = ReliefAssessment
        exclude = ('user',)

        fieldsets = [
            ('Personal Information', {
                'fields': ['first_name',
                           'last_name',
                           'initials',
                           'phone',
                           'phone2',
                           'email',
                           'email2',
                           'dob',
                           'id_number',
                           'issuing_authority',
                           'company',
                           'position_title',
                           'education',
                           'health_insurance',
                           'insurance_provider',
                          ],}),
            ('Disaster Area Address', {
                'fields': ['address',
                           'address2',
                           'city',
                           'state',
                           'zipcode',
                           'country',
                          ],}),
            ('Alternate Address', {
                'fields': ['alt_address',
                           'alt_address2',
                           'alt_city',
                           'alt_state',
                           'alt_zipcode',
                           'alt_country',
                          ],}),
            ('Ethnicity', {
                'fields': ['ethnicity',
                           'other_ethnicity',
                          ],}),
            ('How many in your household are', {
                'fields': ['below_2',
                           'between_3_11',
                           'between_12_18',
                           'between_19_59',
                           'above_60',
                          ],}),
            ('Please identify services needed', {
                'fields': ['ssa',
                           'dhs',
                           'children_needs',
                           'toiletries',
                           'employment',
                           'training',
                           'food',
                           'gas',
                           'prescription',
                           'other_service',
                          ],}),
            ('For Internal Use', {
                'fields': ['case_notes',
                           'items_provided',
                          ],}),
        ]

    def __init__(self, *args, **kwargs):
        if 'edit' in kwargs:
            edit = kwargs.pop('edit', True)
        else:
            edit = True
        super(ReliefAssessmentForm, self).__init__(*args, **kwargs)
        if not edit:
            for name, field in self.fields.items():
                field.widget.attrs['disabled'] = True

        if self.instance.pk:
            self.fields['case_notes'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['items_provided'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['initials'].initial = self.instance.user.profile.initials
            self.fields['phone'].initial = self.instance.user.profile.phone
            self.fields['phone2'].initial = self.instance.user.profile.phone2
            self.fields['email2'].initial = self.instance.user.profile.email2
            self.fields['dob'].initial = self.instance.user.profile.dob
            self.fields['company'].initial = self.instance.user.profile.company
            self.fields['position_title'].initial = self.instance.user.profile.position_title
            self.fields['education'].initial = self.instance.user.profile.education
        else:
            self.fields['case_notes'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['items_provided'].widget.mce_attrs['app_instance_id'] = 0

    def clean(self):
        cleaned_data = self.cleaned_data

        if 'ethnicity' in cleaned_data:
            ethnicity = cleaned_data.get("ethnicity")
            other_text = cleaned_data.get("other_ethnicity")
            if ethnicity == 'other' and not other_text:
                raise forms.ValidationError("Please specify your ethnicity on the text box provided.")

        return cleaned_data

    def save(self, *args, **kwargs):
        relief = super(ReliefAssessmentForm, self).save(commit=False)

        user, created = Profile.get_or_create_user(**{
            'email': self.cleaned_data.get('email'),
            'first_name': self.cleaned_data.get('first_name'),
            'last_name': self.cleaned_data.get('last_name'),
        })

        if created:
            profile = user.profile
            profile.initials = self.cleaned_data.get('initials')
            profile.phone = self.cleaned_data.get('phone')
            profile.phone2 = self.cleaned_data.get('phone2')
            profile.email2 = self.cleaned_data.get('email2')
            profile.dob = self.cleaned_data.get('dob')
            profile.company = self.cleaned_data.get('company')
            profile.position_title = self.cleaned_data.get('position_title')
            profile.education = self.cleaned_data.get('education')
            profile.save()

        relief.user = user
        relief.save()
