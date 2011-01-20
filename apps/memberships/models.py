import operator
import hashlib
import uuid
from hashlib import md5
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from perms.models import TendenciBaseModel
from invoices.models import Invoice
from directories.models import Directory
from user_groups.models import Group
from memberships.managers import MemberAppManager, MemberAppEntryManager
from memberships.managers import MembershipManager
from base.utils import day_validate
from payments.models import PaymentMethod
from user_groups.models import GroupMembership
from haystack.query import SearchQuerySet
import re


FIELD_CHOICES = (
    ("text", _("Text")),
    ("paragraph-text", _("Paragraph Text")),
    ("check-box", _("Checkbox")),
    ("choose-from-list", _("Choose from a list")),
    ("multi-select", _("Multi select")),
    ("file-uploader", _("File upload")),
    ("date", _("Date")),
    ("date-time", _("Date/time")),
    ("first-name", _("First Name")),
    ("last-name", _("Last Name")),
    ("email", _("Email")),
    ("header", _("Section Header")),
    ("description", _(" Description")),
    ("horizontal-rule", _("Horizontal Rule")),
    ("membership-type", _("Membership Type")),
    ("payment-method", _("Payment Method")),
)

OBJECT_TYPE_CHOICES = (
    ("user", _("User")),
    ("membership", _("Membership")),
    ("directory", _("Directory")),
    ("donation", _("Donation")),
    ("custom", _("Custom")),
)
PERIOD_CHOICES = (
    ("fixed", _("Fixed")),
    ("rolling", _("Rolling")),
)
PERIOD_UNIT_CHOICES = (
    ("days", _("Days")),
    ("months", _("Months")),
    ("years", _("Years")),
)

class MembershipType(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.CharField(_('Description'), max_length=500)
    price = models.DecimalField(_('Price'), max_digits=15, decimal_places=2, blank=True, default=0,
        help_text="Set 0 for free membership.")
    renewal_price = models.DecimalField(_('Renewal Price'), max_digits=15, decimal_places=2, 
        blank=True, default=0, null=True, help_text="Set 0 for free membership.")
    # for first time processing
    admin_fee = models.DecimalField(_('Admin Fee'),
        max_digits=15, decimal_places=2, blank=True, default=0, null=True,
        help_text="Admin fee for the first time processing")
    
    group = models.ForeignKey(Group, related_name="membership_types",
        help_text="Members joined will be added to this group")
    
    require_approval = models.BooleanField(_('Require Approval'), default=1)
    allow_renewal = models.BooleanField(_('Allow Renewal'), default=1)
    renewal = models.BooleanField(_('Renewal Only'), default=0)
    order = models.IntegerField(_('Order'), default=0, 
        help_text='Types will be displayed in ascending order based on this field')
    admin_only = models.BooleanField(_('Admin Only'), default=0)  # from allowuseroption
    
    #expiration_method = models.CharField(_('Expiration Method'), max_length=50)
    #expiration_method_custom_dt = models.DateTimeField()
    never_expires = models.BooleanField(_("Never Expires"), default=0,
                                        help_text='If selected, skip the Renewal Options.')
    period = models.IntegerField(_('Period'), default=0)
    period_unit = models.CharField(choices=PERIOD_UNIT_CHOICES, max_length=10)
    period_type = models.CharField(_("Period Type"),default='rolling', choices=PERIOD_CHOICES, max_length=10)
    
    rolling_option = models.CharField(_('Expires On'), max_length=50)
    rolling_option1_day = models.IntegerField(_('Expiration Day'), default=0)
    rolling_renew_option = models.CharField(_('Renewal Expires On'), max_length=50)
    rolling_renew_option1_day = models.IntegerField(default=0)
    rolling_renew_option2_day = models.IntegerField(default=0)
    
    fixed_option = models.CharField(_('Expires On'), max_length=50)
    fixed_option1_day = models.IntegerField(default=0)
    fixed_option1_month = models.IntegerField(default=0)
    fixed_option1_year = models.IntegerField(default=0)
    fixed_option2_day = models.IntegerField(default=0)
    fixed_option2_month = models.IntegerField(default=0)
    
    fixed_option2_can_rollover = models.BooleanField(_("Allow Rollover"), default=0)
    fixed_option2_rollover_days = models.IntegerField(default=0, 
            help_text=_("Membership signups after this date covers the following calendar year as well."))
    
    renewal_period_start = models.IntegerField(_('Renewal Period Start'), default=0, 
            help_text="How long (in days) before the memberships expires can the member renew their membership.")
    renewal_period_end = models.IntegerField(_('Renewal Period End'), default=0, 
            help_text="How long (in days) after the memberships expires can the member renew their membership.")
    expiration_grace_period = models.IntegerField(_('Expiration Grace Period'), default=0, 
            help_text="The number of days after the membership expires their membership is still active.")
   
    #corporate_membership_only = models.BooleanField(_('Corporate Membership Only'), default=0)
    #corporate_membership_type_id = models.IntegerField(_('Corporate Membership Type'), default=0,
    #        help_text='If corporate membership only is checked, select a corporate membership type to associate with.')

    #ma = models.ForeignKey("App", blank=True, null=True)

    class Meta:
        verbose_name = "Membership Type"
        permissions = (("view_membershiptype","Can view membership type"),)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
    
     
    def get_expiration_dt(self, renewal=False, join_dt=None, renew_dt=None):
        """
        Calculate the expiration date - for join or renew (renewal=True)
        
        Examples: 
            
            For join:
            expiration_dt = membership_type.get_expiration_dt(join_dt=membership.join_dt)
            
            For renew:
            expiration_dt = membership_type.get_expiration_dt(renewal=1, 
                                                              join_dt=membership.join_dt,
                                                              renew_dt=membership.renew_dt)
        
        """
        now = datetime.now()
        
        if not join_dt or not isinstance(join_dt, datetime):
            join_dt = now
        if renewal and (not renew_dt or not isinstance(renew_dt, datetime)):
            renew_dt = now
        
        if self.never_expires:
            return None
        
        if self.period_type == 'rolling':
            if self.period_unit == 'days':
                return now + timedelta(days=self.period)
            
            elif self.period_unit == 'months':
                return now + relativedelta(months=self.period)
            
            else: # if self.period_unit == 'years':
                if not renewal:
                    if self.rolling_option == '0':
                        # expires on end of full period
                        return join_dt + relativedelta(years=self.period)
                    else: # self.expiration_method == '1':
                        # expires on ? days at signup (join) month
                        if not self.rolling_option1_day:
                            self.rolling_option1_day = 1
                        expiration_dt = join_dt + relativedelta(years=self.period)
                        self.rolling_option1_day = day_validate(datetime(expiration_dt.year, join_dt.month, 1), 
                                                                    self.rolling_option1_day)
                        
                        return datetime(expiration_dt.year, join_dt.month, 
                                                 self.rolling_option1_day, expiration_dt.hour,
                                                 expiration_dt.minute, expiration_dt.second)
                else: # renewal = True
                    if self.rolling_renew_option == '0':
                        # expires on the end of full period
                        return renew_dt + relativedelta(years=self.period)
                    elif self.rolling_renew_option == '1':
                        # expires on the ? days at signup (join) month
                        if not self.rolling_renew_option1_day:
                            self.rolling_renew_option1_day = 1
                        expiration_dt = renew_dt + relativedelta(years=self.period)
                        self.rolling_renew_option1_day = day_validate(datetime(expiration_dt.year, join_dt.month, 1), 
                                                                    self.rolling_renew_option1_day)
                        return datetime(expiration_dt.year, join_dt.month, 
                                                 self.rolling_renew_option1_day, expiration_dt.hour,
                                                 expiration_dt.minute, expiration_dt.second)
                    else:
                        # expires on the ? days at renewal month
                        if not self.rolling_renew_option2_day:
                            self.rolling_renew_option2_day = 1
                        expiration_dt = renew_dt + relativedelta(years=self.period)
                        self.rolling_renew_option2_day = day_validate(datetime(expiration_dt.year, renew_dt.month, 1), 
                                                                    self.rolling_renew_option2_day)
                        return datetime(expiration_dt.year, renew_dt.month, 
                                                 self.rolling_renew_option2_day, expiration_dt.hour,
                                                 expiration_dt.minute, expiration_dt.second)
                    
                    
        else: #self.period_type == 'fixed':
            if self.fixed_option == '0':
                # expired on the fixed day, fixed month, fixed year
                if not self.fixed_option1_day:
                    self.fixed_option1_day = 1
                if not self.fixed_option1_month:
                    self.fixed_option1_month = 1
                if self.fixed_option1_month > 12:
                    self.fixed_option1_month = 12
                if not self.fixed_option1_year:
                    self.fixed_option1_year = now.year
                    
                self.fixed_option1_day = day_validate(datetime(self.fixed_expiration_year, 
                                                                  self.fixed_expiration_month, 1), 
                                                                    self.fixed_option1_day)
                    
                return datetime(self.fixed_option1_year, self.fixed_option1_month, 
                                self.fixed_option1_day)
            else: # self.fixed_option == '1'
                # expired on the fixed day, fixed month of current year
                if not self.fixed_option2_day:
                    self.fixed_option2_day = 1
                if not self.fixed_option2_month:
                    self.fixed_option2_month = 1
                if self.fixed_option2_month > 12:
                    self.fixed_option2_month = 12
                
                self.fixed_expiration_day2 = day_validate(datetime(now.year, 
                                                                  self.fixed_option2_month, 1), 
                                                                    self.fixed_option2_day)
                
                expiration_dt = datetime(now.year, self.fixed_option2_month,
                                        self.fixed_option2_day)
                if self.fixed_option2_can_rollover:
                    if not self.fixed_option2_rollover_days:
                        self.fixed_option2_rollover_days = 0
                    if (now - expiration_dt).days <= self.fixed_option2_rollover_days:
                        expiration_dt = expiration_dt + relativedelta(years=1)
                        
                return expiration_dt

class Membership(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    member_number = models.CharField(_("Member Number"), max_length=50)
    membership_type = models.ForeignKey("MembershipType", verbose_name=_("Membership Type")) 
    user = models.ForeignKey(User, related_name="memberships")
    directory = models.ForeignKey(Directory, blank=True, null=True) 
    
    renewal = models.BooleanField(default=0)
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField(_("Join Date Time"), null=True)
    renew_dt = models.DateTimeField(_("Renew Date Time"), blank=True, null=True)
    expiration_dt = models.DateTimeField(_("Expiration Date Time"), null=True)
    approved = models.BooleanField(_("Approved"), default=0)
    approved_denied_dt = models.DateTimeField(_("Approved or Denied Date Time"))
    approved_denied_user = models.ForeignKey(User, verbose_name=_("Approved or Denied User"), null=True)
    corporate_membership_id = models.IntegerField(_('Corporate Membership Id'), default=0)
    payment_method = models.CharField(_("Payment Method"), max_length=50)
    
    # add membership application id - so we can support multiple applications
    ma = models.ForeignKey("App")

    objects = MembershipManager()
    
    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        permissions = (("view_membership","Can view membership"),)
    
    def __unicode__(self):
        return "%s #%s" % (self.user.get_full_name(), self.member_number)

    @models.permalink
    def get_absolute_url(self):
        return ('membership.details', [self.pk])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
    
class MembershipArchive(models.Model):
    guid = models.CharField(max_length=50)
    member_number = models.CharField(max_length=50)
    membership_type = models.ForeignKey("MembershipType")
    user = models.ForeignKey(User, related_name="membership_archives")
    
    directory = models.ForeignKey(Directory, blank=True, null=True) 
    
    renewal = models.BooleanField(default=0)
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField() 
    renew_dt = models.DateTimeField() 
    expiration_dt = models.DateTimeField()
    approved = models.BooleanField(default=0)
    approved_denied_dt = models.DateTimeField()
    approved_denied_user_id =  models.IntegerField(default=0)
    # maybe change to foreign key to corporate_membership
    corporate_membership_id = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=50)
    
    ma_id = models.IntegerField()
    
    # these fields should be copied from Membership table
    create_dt = models.DateTimeField()
    update_dt = models.DateTimeField()
    #creator = models.ForeignKey(User, editable=False, related_name="memb_archives_creator")
    creator_id = models.IntegerField(default=0)
    creator_username = models.CharField(max_length=50)
    owner_id = models.IntegerField(default=0)   
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField()
    status_detail = models.CharField(max_length=50)
    
    # the actual archive datetime and user
    archive_dt = models.DateTimeField()
    archive_user = models.ForeignKey(User, related_name="membership_archiver")
    
    def __unicode__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.member_number) 

class App(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)

    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True,
        help_text="Description of this application. Displays at top of application.")
    confirmation_text = models.TextField(_("Confirmation Text"), blank=True, 
        help_text="Text the submitter sees after submitting.")
    notes = models.TextField(blank=True,
        help_text="Extra notes about this application for editors.  Hidden actual application.")
    use_captcha = models.BooleanField(_("Use Captcha"), default=1)

    membership_types = models.ManyToManyField(MembershipType, verbose_name="Membership Types")
    payment_methods = models.ManyToManyField(PaymentMethod, verbose_name="Payment Methods")

    objects = MemberAppManager()

    class Meta:
        verbose_name = "Membership Application"
        permissions = (("view_membership_application","Can view membership application"),)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('membership.application_details', [self.slug])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)

class AppFieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True).order_by('pk')

class AppField(models.Model):
    app = models.ForeignKey("App", related_name="fields")
    content_type = models.ForeignKey(ContentType,
        related_name="membership_app_field_set", editable=False, null=True)
    attribute_name = models.CharField(_("Attribute Name"), max_length=300)
    label = models.CharField(_("Label"), max_length=200)

    description = models.TextField(_("Description"), max_length=200, blank=True)

    help_text = models.CharField(_("Help Text"), max_length=200, blank=True)
    default_value = models.CharField(_("Default Value"), max_length=200, blank=True)
    css_class = models.CharField(_("CSS Class"), max_length=200, blank=True)

    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES, max_length=100)
    vital = models.BooleanField(_("Vital"), default=False, blank=True)
    required = models.BooleanField(_("Required"), default=True, blank=True)
    visible = models.BooleanField(_("Visible"), default=True, blank=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text="Comma separated options where applicable")

    unique = models.BooleanField(_("Unique"), default=True, blank=True)
    admin_only = models.BooleanField(_("Admin Only"), default=False, blank=True)
    position = models.IntegerField(blank=True)

    objects = AppFieldManager()

#    def save(self, *args, **kwargs):
#        if self.position is None:
#            # Append
#            try:
#                last = model.objects.order_by('-position')[0]
#                self.position = last.position + 1
#            except IndexError:
#                # First row
#                self.position = 0
#
#        return super(AppField, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        ordering = ('position',)

    def __unicode__(self):
        return self.label

class AppEntry(models.Model):
    """
    An entry submitted via a membership application.
    """
    app = models.ForeignKey("App", related_name="entries", editable=False)
    user = models.ForeignKey(User, null=True, editable=False)
    membership = models.ForeignKey("Membership", related_name="entries", null=True, editable=False)
    entry_time = models.DateTimeField(_("Date/Time"))

    is_approved = models.NullBooleanField(_('Status'), null=True, editable=False)
    decision_dt = models.DateTimeField(null=True, editable=False)
    judge = models.ForeignKey(User, null=True, related_name='entries', editable=False)

#    create_dt = models.DateTimeField(editable=False)

    objects = MemberAppEntryManager()

    class Meta:
        verbose_name = _("Application Entry")
        verbose_name_plural = _("Application Entries")
        permissions = (("view_appentry","Can view membership application entry"),)

    def __unicode__(self):
        return '%s - Submission #%s' % (self.app, self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ('membership.application_entries', [self.pk])

    @property
    def name(self):
        """Get full name"""
        name = '%s %s' % (self.first_name, self.last_name)
        return name.strip()

    @property
    def first_name(self):
        return self.get_field_value('first-name')

    @property
    def last_name(self):
        return self.get_field_value('last-name')

    @property
    def email(self):
        """Get email string"""
        return self.get_field_value('email')

    def get_field_value(self, field_type):
        try:
            entry_field = self.fields.get(field__field_type=field_type)
            return entry_field.value
        except:
            return ''

    @property
    def hash(self):
        return md5(str(self.pk)).hexdigest()

    @models.permalink
    def hash_url(self):
        return ('membership.application_confirmation', (self.hash,))

    @property
    @models.permalink
    def confirmation_url(self):
        return ('membership.application_confirmation', (self.hash,))

    @property
    def membership_type(self):
        """Get MembershipType object"""

        # TODO: don't like this; would prefer object column in field_entry
        # This is prone to error; We're depending on a string membership type name
        try:
            entry_field = self.fields.get(field__field_type="membership-type")
            membership_type_class = entry_field.field.content_type.model_class()
            return membership_type_class.objects.get(name__exact=entry_field.value.strip())
        except:
            return None

    def payment_method(self):
        """Get PaymentMethod object"""
        # TODO: Figure out how to get the payment_method

    def applicant(self):
        """Get User object"""
        # TODO: Figure out how to get the user

    def approve(self, user, judge):

        # order of suggestions
        # ----------------------
        # auth user
        # fn ln em (match)
        # create new user

        if not user and judge:
            user = judge

        if not isinstance(user, User):

            if isinstance(judge, User):
                user = judge
            elif self.suggested_users():
                user = self.suggested_users()[0]
            else:
                spawned_username = '%s %s' % (app_entry.first_name, app_entry.last_name)
                spawned_username = re.sub('\s+', '_', spawned_username)
                spawned_username = re.sub('[^\w.-]+', '', spawned_username)
                spawned_username = spawned_username.strip('_.- ').lower()

                user = User.objects.create_user(**{
                    'username': spawned_username,
                    'email': self.email,
                    'password': hashlib.sha1(app_entry.email).hexdigest()[:6]
                })

        if instance(judge, User):
            judge_username = judge.username
            judge_pk = judge.pk
        else:
            judge_pk, judge_username = 0, ''

        try: # get membership
            membership = Membership.objects.get(ma=self.app)
        except: # or create membership
            membership = Membership.objects.create(**{
                'member_number': self.app.entries.count(),
                'membership_type': self.membership_type,
                'user':user,
                'renewal': self.membership_type.renewal,
                'join_dt':datetime.now(),
                'renew_dt': None,
                'expiration_dt': self.membership_type.get_expiration_dt(join_dt=datetime.now()),
                'approved': True,
                'approved_denied_dt': datetime.now(),
                'approved_denied_user': judge,
                'payment_method':'',
                'ma':self.app,
                'creator':user,
                'creator_username':user.username,
                'owner':user,
                'owner_username':user.username,
            })

        # create group-membership object
        # this adds the user to the group
        GroupMembership.objects.create(**{
            'group':self.membership_type.group,
            'member':user,
            'creator_id': judge_pk,
            'creator_username': judge_username,
            'owner_id':judge_pk,
            'owner_username':judge_username,
            'status':True,
            'status_detail':'active',
        })

        self.is_approved = True
        self.decision_dt = datetime.now()
        self.judge = judge
        self.membership = membership
        self.save()

    def disapprove(self):
        self.is_approved = False
        self.decision_dt = datetime.now()
        self.judge = judge
        self.save()

    def suggested_users(self, grouping=[('first_name', 'last_name', 'email')]):
        """
            Generate list of suggestions [people]
            Use the authenticated user that filled out the application
            Use the fn, ln, em mentioned within the application

            Grouping Example:
                [('first_name', 'last_name'), ('email',)]
                >> (first_name AND last_name) OR (email)

            Grouping Example:
                [('first_name', 'last_name', 'email)]
                >> (first_name AND last_name AND email)
        """
        user_set = {}

        if self.user:
            user_set[self.user.pk] = ' '.join([
                self.user.first_name,
                self.user.last_name,
                self.user.username,
                self.user.email,
            ])

        query_list = [Q(content=' '.join([getattr(self, item) for item in group])) for group in grouping]

        sqs = SearchQuerySet()
        sqs = sqs.filter(reduce(operator.or_, query_list))
        sqs_users = [sq.object.user for sq in sqs]

        for u in sqs_users:
            user_set[u.pk] = ' '.join([u.first_name, u.last_name, u.username, u.email])

        return user_set.items()

    @property
    def status(self):
        status = 'Pending'

        if self.is_approved == True:
            status = 'Approved'
        elif self.is_approved == False:
            status = 'Disapproved'

        return status

class AppFieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a membership application.
    """
    entry = models.ForeignKey("AppEntry", related_name="fields")
    field = models.ForeignKey("AppField", related_name="field")
    value = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = _("Application Field Entry")
        verbose_name_plural = _("Application Field Entries")