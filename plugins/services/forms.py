from datetime import datetime
from datetime import timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _

from captcha.fields import CaptchaField
from models import Service
from perms.utils import is_admin, is_developer
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class ServiceForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Service._meta.app_label,
        'storme_model':Service._meta.module_name.lower()}))

    resume_url = forms.CharField(
        label=_('Service URL'),
        help_text="Link to an external resume (eg. Google Docs)",
        required=False
    )

    is_agency = forms.BooleanField(
        label=_('Agency'),
        help_text="Are you an agency posting this service?",
        required=False
    )

    requested_duration = forms.ChoiceField(
        label=_('Duration'),
        choices=(('30','30 Days'),('60','60 Days'),('90','90 Days'),),
        help_text="Amount of days you would like your service to stay up.",
        required=False
    )

    captcha = CaptchaField()

    activation_dt = SplitDateTimeField(label=_('Activation Date/Time'),
        initial=datetime.now())

    expiration_dt = SplitDateTimeField(label=_('Expriation Date/Time'),
        initial=(datetime.now() + timedelta(days=30)))

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    
    class Meta:
        model = Service
        fields = (
        'title',
        'slug',
        'description',
        'resume_url',
        'location',
        'skills',
        'experience',
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
        'status',
        'status_detail',
       )

        fieldsets = [('Service Information', {
                      'fields': ['title',
                                 'slug',
                                 'description',
                                 'resume_url',
                                 'location',
                                 'skills',
                                 'experience',
                                 'education',
                                 'tags',
                                 'requested_duration',
                                 'is_agency',
                                 ],
                      'legend': ''
                      }),
                      ('Contact', {
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
                     ('Security Code', {
                      'fields': ['captcha',
                                 ],
                        'classes': ['captcha'],
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['activation_dt',
                                 'expiration_dt',
                                 'syndicate',
                                 'status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]
    
    def __init__(self, *args, **kwargs): 
        super(ServiceForm, self).__init__(*args, **kwargs)
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
                'group_perms',
                'activation_dt',
                'expiration_dt',
                'syndicate',
                'status',
                'status_detail'
            ]
        else:
            fields_to_pop += [
               'captcha'
            ]
        if not is_admin(self.user):
            fields_to_pop += [
                'status',
                'status_detail'
            ]
        if not is_developer(self.user):
            fields_to_pop += [
                'status',
            ]
        for f in list(set(fields_to_pop)):
            if f in self.fields: self.fields.pop(f)
        