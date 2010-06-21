from django.db import models
from tagging.fields import TagField
from timezones.fields import TimeZoneField
from perms.models import AuditingBaseModel
from jobs.managers import JobManager
from entities.models import Entity
from tinymce import models as tinymce_models

from uuid import uuid1 

class Job(AuditingBaseModel):
    guid = models.CharField(max_length=40, default=uuid1)
    title = models.CharField(max_length=250)
    description = tinymce_models.HTMLField()
    list_type = models.CharField(max_length=50) #premium or regular

    code = models.CharField(max_length=50) # internal job-code
    location = models.CharField(max_length=500) #cannot be foreign, needs to be open 'Texas' 'All 50 States' 'US and International'
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    level = models.CharField(max_length=50) # e.g. entry, part-time, permanent, contract
    period = models.CharField(max_length=50) # full time, part time, contract
    is_agency = models.BooleanField() #defines if the job posting is by a third party agency
    percent_travel = models.IntegerField() #how much travel is required for the position
    
    contact_method = models.TextField(blank=True) #preferred method - email, phone, fax. leave open field for user to define
    position_reports_to = models.CharField(max_length=200) #manager, CEO, VP, etc
    salary_from = models.CharField(max_length=50) 
    salary_to = models.CharField(max_length=50)
    computer_skills = models.TextField(blank=True)

    # date related fields
    requested_duration = models.IntegerField()# 30, 60, 90 days - should be relational table
    activation_dt = models.DateTimeField(null=True, blank=True) #date job listing was activated 
    post_dt = models.DateTimeField(null=True, blank=True) #date job was posted (same as create date?)
    expiration_dt = models.DateTimeField(null=True, blank=True) #date job expires based on activation date and duration
    start_dt = models.DateTimeField(null=True, blank=True) #date job starts(defined by job poster)
    
    job_url = models.CharField(max_length=300) #link to other (fuller) job posting
    
    syndicate = models.BooleanField(blank=True)
    
    # meta information
    design_notes = models.TextField(blank=True)
    page_title = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)

    entity = models.ForeignKey(Entity,null=True)
    entity_owner_id = models.IntegerField(blank=True)
           
    #TO DO - foreign
    contact_company = models.CharField(max_length=300)
    contact_name = models.CharField(max_length=150)
    contact_address = models.CharField(max_length=50)
    contact_address2 = models.CharField(max_length=50)
    contact_city = models.CharField(max_length=50)
    contact_state = models.CharField(max_length=50)
    contact_zip_code = models.CharField(max_length=50)
    contact_country = models.CharField(max_length=50)
    contact_phone = models.CharField(max_length=50)
    contact_fax = models.CharField(max_length=50)
    contact_email = models.CharField(max_length=300)
    contact_website = models.CharField(max_length=300)
    
    create_dt = models.DateTimeField(auto_now_add=True)

    #TO DO - FIGURE OUT CATEGORY
    #category_id = models.IntegerField(null=True, blank=True)
          
    #integrate with payment (later)
    #invoice_id = models.ForeignKey(Invoice, blank=True, null=True)   
    #payment_method = models.CharField(max_length=50)
    #member_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    #member_count = models.IntegerField(blank=True)
    #non_member_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    #non_member_count = models.IntegerField(blank=True)
    #override_price = models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)
    #override_userid = models.IntegerField(null=True, blank=True)
    
    #don't need
    #positionlevel = models.CharField(max_length=250) #does not appear to be in use in T4
    #contactcompanyindustry = models.CharField(max_length=150)
    #duration = models.CharField(max_length=50) #does not appear to be in use in T4
    #citizenship_required = models.BooleanField()
    #security_clearance = models.BooleanField()
    #expertise = models.TextField(blank=True)
    #benefits = models.TextField(blank=True)
    #is_offsite = models.BooleanField(blank=True)
    #language = models.CharField(max_length=200)
 
    objects = JobManager()

    class Meta:
        permissions = (("view_job","Can view job"),)

    @models.permalink
    def get_absolute_url(self):
        return ("job", [self.pk])

    def __unicode__(self):
        return self.headline

