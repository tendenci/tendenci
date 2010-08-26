from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from jobs.models import Job
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField
from jobs.models import JobPricing
from jobs.utils import get_duration_choices, get_payment_method_choices

class JobForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Job._meta.app_label, 
        'storme_model':Job._meta.module_name.lower()}))

    activation_dt = SplitDateTimeField(label=_('Activation Date/Time'),
        initial=datetime.now())

    post_dt = SplitDateTimeField(label=_('Post Date/Time'),
        initial=datetime.now())

    expiration_dt = SplitDateTimeField(label=_('Expriation Date/Time'),
        initial=datetime.now())

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    
    requested_duration = forms.ChoiceField()
    
    list_type = forms.ChoiceField(initial='regular', choices=(('regular','Regular'),
                                                              ('premium', 'Premium'),))
    payment_method = forms.CharField(error_messages={'required': 'Please select a payment method.'})
    
    class Meta:
        model = Job
        fields = (
        'title',
        'slug',
        'description',
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
        'list_type',
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
        'syndicate',
        'status',
        'status_detail',
        'payment_method',
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
        
        if not is_admin(user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
        if self.fields.has_key('payment_method'):
            self.fields['payment_method'].widget = forms.RadioSelect(choices=get_payment_method_choices(user))
        if self.fields.has_key('requested_duration'):
            self.fields['requested_duration'].choices = get_duration_choices()


DURATION_CHOICES = ((14,'14 Days from Activation date'), 
                    (30,'30 Days from Activation date'), 
                    (60,'60 Days from Activation date'), 
                    (90,'90 Days from Activation date'),
                    (120,'120 Days from Activation date'),
                    (180,'180 Days from Activation date'),
                    (365,'365 Days from Activation date'),
                    )
STATUS_CHOICES = ((1, 'Active'),
                   (0, 'Inactive'),)
       
class JobPricingForm(forms.ModelForm): 
    duration = forms.ChoiceField(initial=14, choices=DURATION_CHOICES)
    status = forms.ChoiceField(initial=1, choices=STATUS_CHOICES, required=False)
    class Meta:
        model = JobPricing
        fields = ('duration',
                  'regular_price',
                  'premium_price',
                  'regular_price_member',
                  'premium_price_member',
                  'show_member_pricing',
                  'status',)
    
        