from __future__ import print_function
from datetime import datetime
from datetime import timedelta
from os.path import splitext

from django import forms
from django.utils.translation import ugettext_lazy as _

from captcha.fields import CaptchaField
from tendenci.apps.resumes.models import Resume
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.base.fields import SplitDateTimeField
from tendenci.apps.base.fields import EmailVerificationField, CountrySelectField

ALLOWED_FILE_EXT = (
    '.doc',
    '.docx',
    '.pdf',
    '.rtf'
)

class ResumeForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Resume._meta.app_label,
        'storme_model':Resume._meta.model_name.lower()}))

    resume_url = forms.CharField(
        label=_('Resume URL'),
        help_text=_("Link to an external resume (eg. Google Docs)"),
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

    captcha = CaptchaField(label=_('Type the code below'))

    contact_email = EmailVerificationField(label=_("Contact email"), required=False)
    contact_country = CountrySelectField(label=_("Contact country"), required=False)

    activation_dt = SplitDateTimeField(label=_('Activation Date/Time'),
        initial=datetime.now())

    expiration_dt = SplitDateTimeField(label=_('Expriation Date/Time'),
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
        'contact_name',
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
                      'fields': ['contact_name',
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

        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

        # adjust fields depending on user status
        fields_to_pop = []
        if not self.user.is_authenticated():
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
