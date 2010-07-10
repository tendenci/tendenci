from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from jobs.models import Job
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class JobForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Job._meta.app_label, 
        'storme_model':Job._meta.module_name.lower()}))

    activation_dt = SplitDateTimeField(label=_('Release Date/Time'),
        initial=datetime.now())

    post_dt = SplitDateTimeField(label=_('Post Date/Time'),
        initial=datetime.now())

    expiration_dt = SplitDateTimeField(label=_('Expriation Date/Time'),
        initial=datetime.now())
    
    class Meta:
        model = Job
        fields = (
        'title',
        'slug',
        'description',
        'list_type',
        'code',
        'location',
        'skills',
        'experience',
        'education',
        'level',
        'period',
        'is_agency',
        'percent_travel',
        'contact_method',
        'position_reports_to',
        'salary_from',
        'salary_to',
        'computer_skills',
        'requested_duration',
        'activation_dt',
        'post_dt',
        'expiration_dt',
        'job_url',
        'syndicate',
        'design_notes',
        'entity',
        'contact_company',
        'contact_name',
        'contact_address',
        'contact_address2',
        'contact_city',
        'contact_state',
        'contact_zip_code',
        'contact_country',
        'contact_phone',
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
 
    #integrate with payment (later)
    #invoice_id  
    #payment_method
    #member_price
    #member_count
    #non_member_price
    #non_member_count
    #override_price
    #override_userid
    
    #don't need
    #contactcompanyindustry
    #duration
    #citizenship_required
    #security_clearance
    #expertise
    #benefits
    #is_offsite
    #language

    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(JobForm, self).__init__(user, *args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0        
        
        
        