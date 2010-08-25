from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from resumes.models import Resume
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class ResumeForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Resume._meta.app_label, 
        'storme_model':Resume._meta.module_name.lower()}))

    activation_dt = SplitDateTimeField(label=_('Activation Date/Time'),
        initial=datetime.now())

    post_dt = SplitDateTimeField(label=_('Post Date/Time'),
        initial=datetime.now())

    expiration_dt = SplitDateTimeField(label=_('Expriation Date/Time'),
        initial=datetime.now())

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    
    class Meta:
        model = Resume
        fields = (
        'title',
        'slug',
        'description',
        'list_type',
        'location',
        'skills',
        'experience',
        'education',
        'is_agency',
        'requested_duration',
        'activation_dt',
        'post_dt',
        'expiration_dt',
        'resume_url',
        'syndicate',
        'design_notes',
        'entity',
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
        'tags',        
        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
        'allow_user_edit',
        'allow_member_edit',
        'status',
        'status_detail',
       )
 
    
    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(ResumeForm, self).__init__(user, *args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0        
        
        if not is_admin(user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
        