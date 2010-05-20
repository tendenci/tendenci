from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from timezones.fields import TimeZoneField
from base.models import AuditingBase

class Profile(AuditingBase):
    # relations
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    
    guid = models.CharField(max_length=50)
    entity_id = models.IntegerField(default=1)
    pl_id = models.IntegerField(default=1)
    member_number = models.CharField(_('member number'), max_length=50)
    historical_member_number = models.CharField(_('historical member number'), max_length=50)
    
    # profile meta data
    time_zone = TimeZoneField(_('timezone'))
    language = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    salutation = models.CharField(_('salutation'), max_length=15, blank=True)
    initials = models.CharField(_('initials'), max_length=50, blank=True)
    display_name = models.CharField(_('display name'), max_length=120, blank=True)
    mailing_name = models.CharField(_('mailing name'), max_length=120, blank=True)
    company = models.CharField(_('company') , max_length=100, blank=True)
    position_title = models.CharField(_('position title'), max_length=50, blank=True)
    position_assignment = models.CharField(_('position assignment'), max_length=50, blank=True)
    sex = models.CharField(_('sex'), max_length=50, choices=(('male', u'Male'),('female', u'Female')))
    address_type = models.CharField(_('address type'), max_length=50, blank=True)
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zipcode = models.CharField(_('zipcode'), max_length=50, blank=True)
    country = models.CharField(_('country'), max_length=50, blank=True)
    county = models.CharField(_('county'), max_length=50, blank=True)
    phone = models.CharField(_('phone'), max_length=50, blank=True)
    phone2 = models.CharField(_('phone2'), max_length=50, blank=True)
    fax = models.CharField(_('fax'), max_length=50, blank=True)
    work_phone = models.CharField(_('work phone'), max_length=50, blank=True)
    home_phone = models.CharField(_('home phone'), max_length=50, blank=True)
    mobile_phone = models.CharField(_('phone2'), max_length=50, blank=True)
    email = models.CharField(_('email'), max_length=200,  blank=True)
    email2 = models.CharField(_('email2'), max_length=200,  blank=True)
    url = models.CharField(_('url'), max_length=100, blank=True)
    url2 = models.CharField(_('url2'), max_length=100, blank=True)
    dob = models.DateTimeField(_('date of birth'), null=True, blank=True)
    ssn = models.CharField(_('social security number'), max_length=50, blank=True)
    spouse = models.CharField(_('spouse'), max_length=50, blank=True)
    department = models.CharField(_('department'), max_length=50, blank=True)
    education = models.CharField(_('education'), max_length=100, blank=True)
    student = models.IntegerField(_('student'), null=True, blank=True)
    remember_login = models.BooleanField(_('remember login'))
    exported = models.BooleanField(_('exported'))
    direct_mail = models.BooleanField(_('direct mail'), default=False)
    notes = models.TextField(_('notes'), blank=True) 
    admin_notes = models.TextField(_('admin notes'), blank=True) 
    referral_source = models.CharField(_('referral source'), max_length=50, blank=True)
    hide_in_search = models.BooleanField()
    hide_address = models.BooleanField()
    hide_email = models.BooleanField()
    hide_phone = models.BooleanField()   
    first_responder = models.BooleanField(_('first responder'))
    agreed_to_tos = models.BooleanField(_('agrees to tos'))
    
    # date fields
    create_dt = models.DateTimeField(auto_now_add=True)
    submit_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    
