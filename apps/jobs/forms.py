from jobs.models import Job
from perms.forms import TendenciBaseForm

class JobForm(TendenciBaseForm):
    class Meta:
        model = Job
        fields = (
        'title',
        'description',
#        'position_title',
        'list_type',
#        'position_title',
        'code',
#        'timezone',
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
        'page_title',
        'meta_keywords',
        'meta_description',
#        'entity_id',
#        'entityownerid',
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
        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
        'allow_anonymous_edit',
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
    
    #TO DO - FIGURE OUT CATEGORY
    #category_id
  
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
        
        
        
        