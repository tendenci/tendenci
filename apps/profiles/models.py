import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes import generic

from timezones.fields import TimeZoneField
from perms.models import TendenciBaseModel
from entities.models import Entity
from perms.object_perms import ObjectPermission

from profiles.managers import ProfileManager, ProfileActiveManager


class Profile(TendenciBaseModel):
    # relations
    user = models.OneToOneField(User, related_name="profile", verbose_name=_('user'))
    guid = models.CharField(max_length=40)
    entity = models.ForeignKey(Entity, blank=True, null=True)
    pl_id = models.IntegerField(default=1)
    member_number = models.CharField(_('member number'), max_length=50, blank=True)
    historical_member_number = models.CharField(_('historical member number'), max_length=50, blank=True)

    # profile meta data
    time_zone = TimeZoneField(_('timezone'))
    language = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    salutation = models.CharField(_('salutation'), max_length=15, blank=True, choices=(
                                                                                      ('Mr.', 'Mr.'),
                                                                                      ('Mrs.', 'Mrs.'),
                                                                                      ('Ms.', 'Ms.'),
                                                                                      ('Miss', 'Miss'),
                                                                                      ('Dr.', 'Dr.'),
                                                                                      ('Prof.', 'Prof.'),
                                                                                      ('Hon.', 'Hon.'),
                                                                                      ))
    initials = models.CharField(_('initials'), max_length=50, blank=True)
    display_name = models.CharField(_('display name'), max_length=120, blank=True)
    mailing_name = models.CharField(_('mailing name'), max_length=120, blank=True)
    company = models.CharField(_('company') , max_length=100, blank=True)
    position_title = models.CharField(_('position title'), max_length=50, blank=True)
    position_assignment = models.CharField(_('position assignment'), max_length=50, blank=True)
    sex = models.CharField(_('sex'), max_length=50, blank=True, choices=(('male', u'Male'),('female', u'Female')))
    address_type = models.CharField(_('address type'), max_length=50, blank=True)
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, default='', blank=True)
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
    mobile_phone = models.CharField(_('mobile phone'), max_length=50, blank=True)
    #email = models.CharField(_('email'), max_length=200,  blank=True)
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
    hide_in_search = models.BooleanField(default=False)
    hide_address = models.BooleanField(default=False)
    hide_email = models.BooleanField(default=False)
    hide_phone = models.BooleanField(default=False)   
    first_responder = models.BooleanField(_('first responder'), default=False)
    agreed_to_tos = models.BooleanField(_('agrees to tos'), default=False)
    original_username = models.CharField(max_length=50)
    
    perms = generic.GenericRelation(ObjectPermission,
        object_id_field="object_id", content_type_field="content_type")
    
    objects = ProfileManager()
    actives = ProfileActiveManager()
    
    def __unicode__(self):
        return self.user.username
    
    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.user.username])

    def _can_login(self):
        """
        Private function used to verify active statuses in
        user and profile records.
        """
        return all([self.user.is_active, self.status, self.status_detail == "active"])

    @property
    def is_active(self):
        return self._can_login()

    @property
    def is_member(self):
        if self.member_number and self._can_login():
            return True
        return False

    @property
    def is_staff(self):
        if self.is_superuser:
            return True
        return all([self._can_login(), self.user.is_staff])

    @property
    def is_superuser(self):
        return all([self._can_login(), self.user.is_superuser])

    class Meta:
        permissions = (("view_profile","Can view profile"),)
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        from campaign_monitor.utils import update_subscription
        if not self.id:
            self.guid = str(uuid.uuid1())

        # match allow_anonymous_view with opposite of hide_in_search
        if self.hide_in_search:
            self.allow_anonymous_view = False
        else:
            self.allow_anonymous_view = True

        super(Profile, self).save(*args, **kwargs)
        
        if hasattr(self, 'old_email') and getattr(self, 'old_email') != self.user.email:
            update_subscription(self, self.old_email)
            del self.old_email
        
    # if this profile allows view by user2_compare
    def allow_view_by(self, user2_compare):
        boo = False
       
        if user2_compare.is_superuser:
            boo = True
        else: 
            if user2_compare == self.user:
                boo = True
            else:
                if self.creator == user2_compare or self.owner == user2_compare:
                    if self.status == 1:
                        boo = True
                else:
                    if user2_compare.has_perm('profiles.view_profile', self):
                        boo = True
            
        return boo
    
    # if this profile allows edit by user2_compare
    def allow_edit_by(self, user2_compare):
        if user2_compare.is_superuser:
            return True
        else: 
            if user2_compare == self.user:
                return True
            else:
                if self.creator == user2_compare or self.owner == user2_compare:
                    if self.status == 1:
                        return True
                else:
                    if user2_compare.has_perm('profiles.change_profile', self):
                        return True
        return False

    def get_groups(self):
        memberships = self.user.group_member.all()
        return [membership.group for membership in memberships]

    def roles(self):
        role_set = []

        if self.is_superuser:
            role_set.append('superuser')

        if self.is_staff:
            role_set.append('staff')

        if self.is_member:
            role_set.append('member')

        if self.is_active:
            role_set.append('user')

        return role_set or ['disabled']

    def highest_role(self):
        """
        The highest role will be returned.
        """
        roles = ['superuser', 'staff', 'member', 'user', 'disabled']
        for role in roles:
            if role in self.roles():
                return role

