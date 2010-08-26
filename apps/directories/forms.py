import imghdr
from os.path import splitext

from django import forms

from directories.models import Directory, DirectoryPricing
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE

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
            'allow_anonymous_view',
            'allow_user_view',
            'allow_user_edit',
            'syndicate',
            'status',
            'status_detail',
        )

    def clean_logo(self):
        logo = self.cleaned_data['logo']
        extension = splitext(logo.name)[1]
        
        # check the extension
        if extension.lower() not in ALLOWED_LOGO_EXT:
            raise forms.ValidationError('The logo must be of jpg, gif, or png image type.')
        
        # check the image header
        image_type = '.%s' % imghdr.what('', logo.read())
        if image_type not in ALLOWED_LOGO_EXT:
            raise forms.ValidationError('The logo is an invalid image. Try uploading another logo.')
        
        return logo

    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(DirectoryForm, self).__init__(user, *args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0

        if not is_admin(user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

DURATION_CHOICES = ((14,'14 Days from Activation date'), 
                    (30,'30 Days from Activation date'), 
                    (60,'60 Days from Activation date'), 
                    (90,'90 Days from Activation date'),
                    (120,'120 Days from Activation date'),
                    (365,'1 Year from Activation date'),
                    )
STATUS_CHOICES = ((1, 'Active'),
                   (0, 'Inactive'),)
            
class DirectoryPricingForm(forms.ModelForm): 
    duration = forms.ChoiceField(initial=14, choices=DURATION_CHOICES)
    status = forms.ChoiceField(initial=1, choices=STATUS_CHOICES, required=False)
    class Meta:
        model = DirectoryPricing
        fields = ('duration',
                  'regular_price',
                  'premium_price',
                  'category_threshold',
                  'status',)

