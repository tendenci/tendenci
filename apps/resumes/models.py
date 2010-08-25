import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from base.fields import SlugField
from perms.models import TendenciBaseModel 
from resumes.managers import ResumeManager
from entities.models import Entity
from tinymce import models as tinymce_models
from meta.models import Meta as MetaTags
from resumes.module_meta import ResumeMeta

class Resume(TendenciBaseModel ):
    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=250)
    slug = SlugField(_('URL Path'), unique=True)  
    description = tinymce_models.HTMLField()
    list_type = models.CharField(max_length=50) #premium or regular

    location = models.CharField(max_length=500) #cannot be foreign, needs to be open 'Texas' 'All 50 States' 'US and International'
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    is_agency = models.BooleanField() #defines if the resume posting is by a third party agency
    show_contact_info = models.BooleanField() #display name/address/etc on view page
 
    #TODO: do we need these fields?
    #desiredlocationstate = models.CharField(max_length=50)
    #desiredlocationcountry = models.CharField(max_length=50)
    #willingtorelocate = models.BooleanField()
    #workschedulepreferred = models.CharField(max_length=100)
    #compensationdesired = models.CharField(max_length=50)
    #licenses = models.CharField(max_length=100)
    #certifications = models.CharField(max_length=100)
    #expertise = models.CharField(max_length=800)
    #languages = models.CharField(max_length=120)
     
    # date related fields
    requested_duration = models.IntegerField()# 30, 60, 90 days - should be relational table
    activation_dt = models.DateTimeField(null=True, blank=True) #date resume listing was activated 
    post_dt = models.DateTimeField(null=True, blank=True) #date resume was posted (same as create date?)
    expiration_dt = models.DateTimeField(null=True, blank=True) #date resume expires based on activation date and duration

    resume_url = models.CharField(max_length=300, blank=True) #link to other (fuller) resume posting    
    syndicate = models.BooleanField(blank=True)
    design_notes = models.TextField(blank=True)
           
    #TODO: foreign
    contact_name = models.CharField(max_length=150, blank=True)
    contact_address = models.CharField(max_length=50, blank=True)
    contact_address2 = models.CharField(max_length=50, blank=True)
    contact_city = models.CharField(max_length=50, blank=True)
    contact_state = models.CharField(max_length=50, blank=True)
    contact_zip_code = models.CharField(max_length=50, blank=True)
    contact_country = models.CharField(max_length=50, blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_phone2 = models.CharField(max_length=50, blank=True)    
    contact_fax = models.CharField(max_length=50, blank=True)
    contact_email = models.CharField(max_length=300, blank=True)
    contact_website = models.CharField(max_length=300, blank=True)
 
    meta = models.OneToOneField(MetaTags, null=True)
    entity = models.ForeignKey(Entity,null=True)
    tags = TagField(blank=True)
    
    #TODO: integrate with user
    #user = models.ForeignKey(User,null=True)
                 
    objects = ResumeManager()

    class Meta:
        permissions = (("view_resume","Can view resume"),)

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return ResumeMeta().get_meta(self, name)

    @models.permalink
    def get_absolute_url(self):
        return ("resume", [self.slug])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            
        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

