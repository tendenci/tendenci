import imghdr
from datetime import datetime
from os.path import splitext, basename

from django import forms

from directories.models import Directory, DirectoryPricing
from directories.utils import get_payment_method_choices, get_duration_choices
from perms.utils import is_admin, is_developer
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png' 
)   
                    
class DirectoryForm(TendenciBaseForm):
    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Directory._meta.app_label, 
        'storme_model':Directory._meta.module_name.lower()}))
    
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    
    requested_duration = forms.ChoiceField()
    
    list_type = forms.ChoiceField(initial='regular', choices=(('regular','Regular'),
                                                              ('premium', 'Premium'),))
    payment_method = forms.CharField(error_messages={'required': 'Please select a payment method.'})
    remove_photo = forms.BooleanField(label='Remove the current logo', required=False)

    activation_dt = SplitDateTimeField(initial=datetime.now())
    expiration_dt = SplitDateTimeField(initial=datetime.now())
    
    class Meta:
        model = Directory
        fields = (
            'headline',
            'slug',
            'summary',
            'body',
            'logo',
            'source',
            'timezone',
            'first_name',
            'last_name',
            'address',
            'address2',
            'city',
            'state',
            'zip_code',
            'country',
            'phone',
            'phone2',
            'fax',
            'email',
            'email2',
            'website',
            'tags',
            'requested_duration',
            'list_type',
            'payment_method',
            'activation_dt',
            'expiration_dt',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_user_edit',
            'syndicate',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [('Directory Information', {
                      'fields': ['headline',
                                 'slug',
                                 'summary',
                                 'body',
                                 'logo',
                                 'tags',
                                 'source', 
                                 'timezone',
                                 'activation_dt',
                                 'requested_duration',
                                 'expiration_dt',
                                 ],
                      'legend': ''
                      }),
                      ('Payment', {
                      'fields': ['list_type',
                                 'payment_method'
                                 ],
                        'classes': ['payment_method'],
                      }),
                      ('Contact', {
                      'fields': ['first_name',
                                 'last_name',
                                  'address',
                                  'address2',
                                  'city',
                                  'state',
                                  'zip_code',
                                  'country',
                                  'phone',
                                  'phone2',
                                  'fax',
                                  'email',
                                  'email2',
                                  'website'
                                 ],
                        'classes': ['contact'],
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['syndicate',
                                 'status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]   
        
    def clean_logo(self):
        logo = self.cleaned_data['logo']
        if logo:
            extension = splitext(logo.name)[1]
            
            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The logo must be of jpg, gif, or png image type.')

            # check the image header
            image_type = '.%s' % imghdr.what('', logo.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The logo is an invalid image. Try uploading another logo.')

        return logo

    def __init__(self, *args, **kwargs):
        super(DirectoryForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            if is_admin(self.user):
                self.fields['status_detail'].choices = (('active','Active'),
                                                        ('inactive','Inactive'), 
                                                        ('pending','Pending'),
                                                        ('paid - pending approval', 'Paid - Pending Approval'),)
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0

        if self.instance.logo:
            self.fields['logo'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current logo: <a target="_blank" href="/site_media/media/%s">%s</a>' % (self.instance.logo, basename(self.instance.logo.file.name))
        else:
            self.fields.pop('remove_photo')

        if not is_admin(self.user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        if not is_developer(self.user):
            if 'status' in self.fields: self.fields.pop('status')

        if self.fields.has_key('payment_method'):
            self.fields['payment_method'].widget = forms.RadioSelect(choices=get_payment_method_choices(self.user))
        if self.fields.has_key('requested_duration'):
            self.fields['requested_duration'].choices = get_duration_choices()

    def save(self, *args, **kwargs):
        directory = super(DirectoryForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            directory.logo = None
        return directory

DURATION_CHOICES = (
    (14,'14 Days from Activation date'), 
    (30,'30 Days from Activation date'), 
    (60,'60 Days from Activation date'), 
    (90,'90 Days from Activation date'),
    (120,'120 Days from Activation date'),
    (365,'1 Year from Activation date'),
)
ADMIN_DURATION_CHOICES = (
    (0, 'Unlimited'),
    (14,'14 Days from Activation date'), 
    (30,'30 Days from Activation date'), 
    (60,'60 Days from Activation date'), 
    (90,'90 Days from Activation date'),
    (120,'120 Days from Activation date'),
    (365,'1 Year from Activation date'),
)

STATUS_CHOICES = (
    (1, 'Active'),
    (0, 'Inactive'),
)

class DirectoryPricingForm(forms.ModelForm):
    status = forms.ChoiceField(initial=1, choices=STATUS_CHOICES, required=False)
    
    class Meta:
        model = DirectoryPricing
        fields = ('duration',
                  'regular_price',
                  'premium_price',
                  'category_threshold',
                  'status',)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DirectoryPricingForm, self).__init__(*args, **kwargs)
        if user and is_admin(user):
            self.fields['duration'] = forms.ChoiceField(initial=14, choices=ADMIN_DURATION_CHOICES)
        else:
            self.fields['duration'] = forms.ChoiceField(initial=14, choices=DURATION_CHOICES)

