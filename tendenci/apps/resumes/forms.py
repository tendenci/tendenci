
from datetime import datetime
from datetime import timedelta
from os.path import splitext

from django import forms
from django.utils.translation import ugettext_lazy as _

# from captcha.fields import CaptchaField
from tendenci.apps.resumes.models import Resume
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.base.fields import EmailVerificationField, CountrySelectField
from tendenci.apps.base.forms import CustomCatpchaField
from tendenci.apps.base.forms import FormControlWidgetMixin

ALLOWED_FILE_EXT = (
    '.doc',
    '.docx',
    '.pdf',
    '.rtf'
)

class ResumeSearchForm(forms.Form):
    SEARCH_CRITERIA_CHOICES = (
                        ('', _('SELECT ONE')),
                        ('title', _('Title')),
                        ('description', _('Description')),
                        ('location', _('Location')),
                        ('contact_city', _('City')),
                        ('contact_state', _('State')),
                        ('contact_zip_code', _('Zip Code')),
                        ('contact_country', _('Country')),
                        )
    SEARCH_METHOD_CHOICES = (
                             ('starts_with', _('Starts With')),
                             ('contains', _('Contains')),
                             ('exact', _('Exact')),
                             )
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(label=_("Email"), required=False)
    search_criteria = forms.ChoiceField(choices=SEARCH_CRITERIA_CHOICES,
                                        required=False)
    search_text = forms.CharField(max_length=100, required=False)
    search_method = forms.ChoiceField(choices=SEARCH_METHOD_CHOICES,
                                        required=False)
    grid_view = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ResumeSearchForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': _('Exact Match Search')})
        self.fields['last_name'].widget.attrs.update({'placeholder': _('Exact Match Search')})
        self.fields['email'].widget.attrs.update({'placeholder': _('Exact Match Search')})
        
        for field in self.fields:
            if field not in ['search_criteria', 'search_text', 'search_method', 'grid_view']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class ResumeForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Resume._meta.app_label,
        'storme_model':Resume._meta.model_name.lower()}))

    resume_url = forms.CharField(
        label=_('Resume URL'),
        help_text=_("Link to an external resume (eg. LinkedIn)"),
        required=False
    )

    is_agency = forms.BooleanField(
        label=_('Agency'),
        help_text=_("Are you an agency posting this resume?"),
        required=False
    )

    requested_duration = forms.ChoiceField(
        label=_('Duration'),
        choices=(('30',_('30 Days')),('60',_('60 Days')),('90',_('90 Days')),),
        help_text=_("Amount of days you would like your resume to stay up."),
        required=False
    )

    captcha = CustomCatpchaField(label=_('Type the code below'))

    contact_email = EmailVerificationField(label=_("Email"), required=False)
    contact_country = CountrySelectField(label=_("Country"), required=False)
    contact_address = forms.CharField(label=_("Address"), required=False)
    contact_address2 = forms.CharField(label=_("Address2"), required=False)
    contact_city = forms.CharField(label=_("City"), required=False)
    contact_zip_code = forms.CharField(label=_("Zip code"), required=False)
    contact_country = forms.CharField(label=_("Country"), required=False)
    contact_phone = forms.CharField(label=_("Phone"), required=False)
    contact_phone2 = forms.CharField(label=_("Phone2"), required=False)
    contact_fax = forms.CharField(label=_("Fax"), required=False)
    contact_website = forms.CharField(label=_("Website"), required=False)

    activation_dt = forms.SplitDateTimeField(label=_('Activation Date/Time'),
        initial=datetime.now())

    expiration_dt = forms.SplitDateTimeField(label=_('Expriation Date/Time'),
        initial=(datetime.now() + timedelta(days=30)))

    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

    class Meta:
        model = Resume
        fields = (
        'title',
        'slug',
        'description',
        'resume_url',
        'resume_file',
        'location',
        'skills',
        'experience',
        'awards',
        'education',
        'is_agency',
        'requested_duration',
        'tags',
        'first_name',
        'last_name',
        'contact_address',
        'contact_address2',
        'contact_city',
        'contact_state',
        'contact_zip_code',
        'contact_country',
        'contact_phone',
        'contact_phone2',
        'contact_fax',
        'contact_email',
        'contact_website',
        'captcha',
        'allow_anonymous_view',
        'user_perms',
        'group_perms',
        'activation_dt',
        'expiration_dt',
        'syndicate',
        'status_detail',
       )

        fieldsets = [(_('Resume Information'), {
                      'fields': ['title',
                                 'slug',
                                 'description',
                                 'resume_url',
                                 'resume_file',
                                 'location',
                                 'skills',
                                 'experience',
                                 'awards',
                                 'education',
                                 'tags',
                                 'requested_duration',
                                 'is_agency',
                                 ],
                      'legend': ''
                      }),
                      (_('Contact'), {
                      'fields': ['first_name',
                                 'last_name',
                                 'contact_address',
                                 'contact_address2',
                                 'contact_city',
                                 'contact_state',
                                 'contact_zip_code',
                                 'contact_country',
                                 'contact_phone',
                                 'contact_phone2',
                                 'contact_fax',
                                 'contact_email',
                                 'contact_website',
                                 ],
                        'classes': ['contact'],
                      }),
                     (_('Security Code'), {
                      'fields': ['captcha',
                                 ],
                        'classes': ['captcha'],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['activation_dt',
                                 'expiration_dt',
                                 'syndicate',
                                 'status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(ResumeForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

        # adjust fields depending on user status
        fields_to_pop = []
        if not self.user.is_authenticated:
            fields_to_pop += [
                'allow_anonymous_view',
                'user_perms',
                'member_perms',
                'group_perms',
                'activation_dt',
                'expiration_dt',
                'syndicate',
                'status_detail'
            ]
        else:
            fields_to_pop += [
               'captcha'
            ]
        if not self.user.profile.is_superuser:
            fields_to_pop += [
                'allow_anonymous_view',
                'user_perms',
                'member_perms',
                'group_perms',
                'activation_dt',
                'expiration_dt',
                'syndicate',
                'status_detail'
            ]

            # Populate contact info for non-superuser
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['contact_address'].initial = self.user.profile.address
            self.fields['contact_address2'].initial = self.user.profile.address2
            self.fields['contact_city'].initial = self.user.profile.city
            self.fields['contact_state'].initial = self.user.profile.state
            self.fields['contact_zip_code'].initial = self.user.profile.zipcode
            self.fields['contact_country'].initial = self.user.profile.country
            self.fields['contact_phone'].initial = self.user.profile.phone
            self.fields['contact_phone2'].initial = self.user.profile.phone2
            self.fields['contact_fax'].initial = self.user.profile.fax
            self.fields['contact_email'].initial = self.user.email
            self.fields['contact_website'].initial = self.user.profile.url
            
        for f in list(set(fields_to_pop)):
            if f in self.fields: self.fields.pop(f)

    def clean_syndicate(self):
        """
        clean method for syndicate added due to the update
        done on the field BooleanField -> NullBooleanField
        NOTE: BooleanField is converted to NullBooleanField because
        some Boolean data has value of None than False. This was updated
        on Django 1.6. BooleanField cannot have a value of None.
        """
        data = self.cleaned_data.get('syndicate', False)
        if data:
            return True
        else:
            return False

    def clean_resume_file(self):
        resume = self.cleaned_data['resume_file']
        if resume:
            extension = splitext(resume.name)[1]
            # check the extension
            if extension.lower() not in ALLOWED_FILE_EXT:
                raise forms.ValidationError(_('The file must be of doc, docx, pdf, or rtf format.'))
        return resume

    def clean(self):
        cleaned_data = super(ResumeForm, self).clean()

        print(self.errors)

        return cleaned_data


class ResumeExportForm(FormControlWidgetMixin, forms.Form):
    start_dt = forms.DateField(
                label=_('From'),
                initial=datetime.now()-timedelta(days=365))

    end_dt = forms.DateField(
                label=_('To'),
                initial=datetime.now())
    include_files = forms.BooleanField(initial=False, required=False)

    def clean_start_dt(self):
        data = self.cleaned_data
        start_dt = data.get('start_dt')
        if not start_dt:
            raise forms.ValidationError(_('Start date is required'))

        return start_dt

    def clean_end_dt(self):
        data = self.cleaned_data
        start_dt = data.get('start_dt')
        end_dt = data.get('end_dt')

        if not end_dt:
            raise forms.ValidationError(_('End date is required'))
        if end_dt <= start_dt:
            raise forms.ValidationError(_('End date must be greater than start date'))

        return end_dt
