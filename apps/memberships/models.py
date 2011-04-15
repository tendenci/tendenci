import re
import operator
import hashlib
import uuid
from hashlib import md5
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from perms.models import TendenciBaseModel
from invoices.models import Invoice
from directories.models import Directory
from user_groups.models import Group
from memberships.managers import MemberAppManager, MemberAppEntryManager
from tinymce import models as tinymce_models
from memberships.managers import MembershipManager
from base.utils import day_validate
from payments.models import PaymentMethod
from user_groups.models import GroupMembership
from haystack.query import SearchQuerySet
from event_logs.models import EventLog
from perms.utils import get_notice_recipients, is_member


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
    ("corporate_membership_id", _("Corporate Membership ID")),
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
    
    renewal_period_start = models.IntegerField(_('Renewal Period Start'), default=30, 
            help_text="How long (in days) before the memberships expires can the member renew their membership.")
    renewal_period_end = models.IntegerField(_('Renewal Period End'), default=30, 
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
    corporate_membership_id = models.IntegerField(_('Corporate Membership Id'), default=0)
    payment_method = models.CharField(_("Payment Method"), max_length=50)
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
        
    def get_renewal_period_dt(self):
        """
        calculate and return a tuple of renewal period dt (the renewal window):
         (renewal_period_start_dt, renewal_period_end_dt)
         
        """
        if not self.expiration_dt or not isinstance(self.expiration_dt, datetime):
            return (None, None)
        
        start_dt = self.expiration_dt - timedelta(days=self.membership_type.renewal_period_start)
        end_dt = self.expiration_dt + timedelta(days=self.membership_type.renewal_period_end)
        
        return (start_dt, end_dt)
        
    def can_renew(self):

        if self.expiration_dt is None:  # expiration_dt == NULL
            return False

        start_dt, end_dt = self.get_renewal_period_dt()

        # assert that we're within the renewal period
        return (datetime.now() >= start_dt and datetime.now() <= end_dt)

    def get_app_initial(self):
        """
        Get a dictionary of membership application
        initial values.  Used for prefilling out membership
        application forms. Useful for renewals.
        """
        entry = self.ma.entries.order_by('-pk')[0]
        init_kwargs = [(f.field.pk, f.value) for f in entry.fields.all()]
        return dict(init_kwargs)


class MembershipArchive(TendenciBaseModel):
    """
    Keep a record of the old memberships.
    These records are created when a membership is renewed.
    A reference to the newest (non-archived) membership is 
    included via the 'membership' field.
    """
    membership = models.ForeignKey('Membership')
    member_number = models.CharField(_("Member Number"), max_length=50)
    membership_type = models.ForeignKey("MembershipType", verbose_name=_("Membership Type"))
    directory = models.ForeignKey(Directory, blank=True, null=True)
    join_dt = models.DateTimeField(_("Join Date Time"))
    renew_dt = models.DateTimeField(_("Renew Date Time"), null=True)
    expire_dt = models.DateTimeField(_("Expire Date Time"), null=True)
    corporate_membership_id = models.IntegerField(_('Corporate Membership Id'), default=0)
    invoice = models.ForeignKey(Invoice, null=True)
    payment_method = models.CharField(_("Payment Method"), max_length=50)
    ma = models.ForeignKey("App")
    objects = MembershipManager()

    class Meta:
        verbose_name = _("Archived Membership")
        verbose_name_plural = _("Archived Memberships")
        permissions = (("view_archived_membership","Can view archived membership"),)

    def __unicode__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.member_number) 
    
class Notice(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice_name = models.CharField(_("Name"), max_length=250)
    num_days = models.IntegerField(default=0)
    notice_time = models.CharField(_("Notice Time"), max_length=20,
                                   choices=(('before','Before'),
                                            ('after','After'),
                                            ('attimeof','At Time Of'))) 
    notice_type = models.CharField(_("For Notice Type"), max_length=20,
                                   choices=(('join','Join Date'),
                                            ('renewal','Renewal Date'),
                                            ('expiration','Expiration Date'))) 
    system_generated = models.BooleanField(_("System Generated"), default=0)
    membership_type = models.ForeignKey("MembershipType", blank=True, null=True,
                                        help_text=_("Note that if you don't select a membership type, the notice will go out to all members."))
    
    subject =models.CharField(max_length=255)
    content_type = models.CharField(_("Content Type"), 
                                    choices=(('html','HTML'),
                                            ('text','Plain Text')),
                                    max_length=10)
    sender = models.EmailField(max_length=255, blank=True, null=True)
    sender_display = models.CharField(max_length=255, blank=True, null=True)
    email_content = tinymce_models.HTMLField(_("Email Content"))
    
    
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="membership_notice_creator",  null=True)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="membership_notice_owner", null=True)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(choices=(('active','Active'),('admin_hold','Admin Hold')), 
                                     default='active', max_length=50)
    status = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.notice_name
    
    @models.permalink
    def get_absolute_url(self):
        return ('membership.notice_email_content', [self.id])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
        

class NoticeLog(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice = models.ForeignKey(Notice, related_name="logs")
    notice_sent_dt = models.DateTimeField(auto_now_add=True)
    num_sent = models.IntegerField()
    
class NoticeLogRecord(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice_log = models.ForeignKey(NoticeLog, related_name="log_records")
    membership = models.ForeignKey(Membership, related_name="log_records")
    action_taken = models.BooleanField(default=0)
    action_taken_dt = models.DateTimeField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)

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
    
    use_for_corp = models.BooleanField(_("Use for Corporate Individuals"), default=0)

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

    def get_prefill_kwargs(self, membership=None):
        """
        Prefill this application.
        Possible Parameters: user, membership, entry
        """
        entry = membership.ma.entries.order_by('-pk')[0]
        init_kwargs = [(f.field.pk, f.value) for f in entry.fields.all()]

        return dict(init_kwargs)


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
    show_on_site = models.BooleanField(_("Show on Site"), default=False, blank=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text="Comma separated options where applicable")

    unique = models.BooleanField(_("Unique"), default=True, blank=True)
    admin_only = models.BooleanField(_("Admin Only"), default=False, blank=True)
    position = models.IntegerField(blank=True)

    objects = AppFieldManager()

    def save(self, *args, **kwargs):
        if self.position is None:
            # Append
            try:
                last = AppField.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(AppField, self).save(*args, **kwargs)

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

    is_renewal = models.BooleanField(editable=False)
    is_approved = models.NullBooleanField(_('Status'), null=True, editable=False)
    decision_dt = models.DateTimeField(null=True, editable=False)
    judge = models.ForeignKey(User, null=True, related_name='entries', editable=False)

    invoice = models.ForeignKey(Invoice, null=True, editable=False)

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
    
    @property
    def corporate_membership_id(self):
        """Get corporate_membership_id """
        corporate_membership_id = self.get_field_value('corporate_membership_id')
        try:
            corporate_membership_id = int(corporate_membership_id)
        except:
            corporate_membership_id = 0
        return corporate_membership_id

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
        # TODO: Prone to error; We're depending on a string membership type name
        try:
            entry_field = self.fields.get(field__field_type="membership-type")
            membership_type_class = entry_field.field.content_type.model_class()
            return membership_type_class.objects.get(name__exact=entry_field.value.strip())
        except:
            return None

    @property
    def payment_method(self):
        """Get PaymentMethod object"""
        # TODO: don't like this; would prefer object column in field_entry
        # TODO: Prone to error; We're depending on a string membership type name
        try:
            entry_field = self.fields.get(field__field_type="payment-method")
            payment_method_class = entry_field.field.content_type.model_class()
            return payment_method_class.objects.get(human_name__exact=entry_field.value.strip())
        except:
            return None

    def applicant(self):
        """Get User object"""
        if self.membership:
            return self.membership.user

    def approve(self):
        """
        order of candidates (for user-binding)
            authenticated user
            suggestions per fn, ln, em
            new user creation
        """

        # get user -------------
        if self.user and self.user.is_authenticated():
            user = self.user
        elif self.suggested_users():
            user_pk, user_label = self.suggested_users()[0]
            user = User.objects.get(pk=user_pk)
        else:
            user = User.objects.create_user(**{
                'username': self.spawn_username(self.first_name, self.last_name),
                'email': self.email,
                'password': hashlib.sha1(self.email).hexdigest()[:6]
            })

        # get judge --------------
        if self.judge and self.judge.is_authenticated():
            judge, judge_pk, judge_username = self.judge, self.judge.pk, self.judge.username
        else:
            judge, judge_pk, judge_username = None, 0, ''

        # if veteran; create archive
        membership = user.memberships.get_membership()
        if membership:
            archive = MembershipArchive.objects.create(**{
                'membership':membership,
                'member_number': membership.member_number,
                'membership_type': membership.membership_type,
                'directory':membership.directory,
                'join_dt':membership.join_dt,
                'renew_dt':membership.renew_dt,
                'expire_dt':membership.expiration_dt,
                'corporate_membership_id':membership.corporate_membership_id,
                'invoice':membership.invoice,
                'payment_method':membership.payment_method,
                'ma':membership.ma,
                'creator_id':membership.creator_id,
                'creator_username':membership.creator_username,
                'owner_id':membership.owner_id,
                'owner_username':membership.owner_username,
            })

        try: # get membership
            membership = Membership.objects.get(**{
                'membership_type': self.membership_type,
                'user': user,
                'status': True,
                'status_detail': 'active',
            })
        except: # or create membership
            membership = Membership.objects.create(**{
                'member_number': self.app.entries.count(),
                'membership_type': self.membership_type,
                'user':user,
                'renewal': self.membership_type.renewal,
                'join_dt':datetime.now(),
                'renew_dt': None,
                'expiration_dt': self.membership_type.get_expiration_dt(join_dt=datetime.now()),
                'payment_method':'',
                'ma':self.app,
                'corporate_membership_id': self.corporate_membership_id,
                'creator':user,
                'creator_username':user.username,
                'owner':user,
                'owner_username':user.username,
            })

        try:
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
        except:
            pass

        # update user account
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.email = self.email

        try:
            user.get_profile().email = self.email
        except:
            pass

        user.save()

        self.is_approved = True
        self.decision_dt = datetime.now()
        self.membership = membership
        self.save()

    def disapprove(self):

        if self.judge and self.judge.is_authenticated():
            judge, judge_pk, judge_username = self.judge, self.judge.pk, self.judge.username
        else:
            judge, judge_pk, judge_username = None, 0, ''

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
                grouping=[('first_name', 'last_name'), ('email',)]
                (first_name AND last_name) OR (email)

            Grouping Example:
                grouping=[('first_name', 'last_name', 'email)]
                (first_name AND last_name AND email)
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
        sqs = SearchQuerySet().models(User)
        sqs = sqs.filter(reduce(operator.or_, query_list))
        sqs_users = [sq.object.user for sq in sqs]

        for u in sqs_users:
            try:
                user_set[u.pk] = ' '.join([u.first_name, u.last_name, u.username, u.email])
            except:
                pass

        return user_set.items()

    def spawn_username(self, *args):
        """
        Join arguments to create username [string].
        Find similiar usernames; auto-increment newest username.
        Return new username [string].
        """
        if not args:
            raise Exception('spawn_username() requires atleast 1 argument; 0 were given')

        max_length = 4

        un = ' '.join(args)             # concat args into one string
        un = re.sub('\s+','_',un)       # replace spaces w/ underscores
        un = re.sub('[^\w.-]+','',un)   # remove non-word-characters
        un = un.strip('_.- ')           # strip funny-characters from sides
        un = un[:max_length].lower()    # keep max length and lowercase username

        others = [] # find similiar usernames
        for u in User.objects.filter(username__startswith=un):
            if u.username.replace(un, '0').isdigit():
                others.append(int(u.username.replace(un,'0')))

        if others and 0 in others:
            # the appended digit will compromise the username length
            # there would have to be more than 99,999 duplicate usernames
            # to kill the database username max field length
            un = '%s%s' % (un, str(max(others)+1))

        return un.lower()

    @property
    def status(self):
        status = 'Pending'

        if self.is_approved == True:
            status = 'Approved'
        elif self.is_approved == False:
            status = 'Disapproved'

        return status

    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the event sale
        """
        from accountings.models import Acct, AcctEntry, AcctTran
        from accountings.utils import make_acct_entries_initial, make_acct_entries_closing

        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)

            # CREDIT event SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount*(-1))

    # to lookup for the number, go to /accountings/account_numbers/
    def get_acct_number(self, discount=False):
        if discount:
            return 462000
        else:
            return 402000

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """

        # if auto-approve; approve entry; send emails
        # -------------------------------------------

        if not self.membership_type.require_approval:

            self.approve()

            # send email to approved members
            notification.send_emails([self.email],'membership_approved_to_member', {
                'object':self,
                'request':request,
                'membership_total':membership_total,
            })

            # send email to admins
            recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
            if recipients and notification:
                notification.send_emails(recipients,'membership_approved_to_admin', {
                    'object':self,
                    'request':request,
                    'membership_total':membership_total,
                })

            # log entry approval
            EventLog.objects.log(**{
                'event_id' : 1082101,
                'event_data': '%s (%d) approved by %s' % (self._meta.object_name, self.pk, self.judge),
                'description': '%s viewed' % self._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': self,
            })

    def save_invoice(self, **kwargs):
        status_detail = kwargs.get('status_detail', 'estimate')

        print 'app_label', self._meta.app_label
        print 'module_name', self._meta.module_name

        content_type = ContentType.objects.get(app_label=self._meta.app_label,
              model=self._meta.module_name)

        try: # get invoice
            invoice = Invoice.objects.get(
                object_type = content_type,
                object_id = self.pk,
            )
        except: # else; create invoice
            # cannot use get_or_create method
            # because too many fields are required
            invoice = Invoice()
            invoice.object_type = content_type
            invoice.object_id = self.pk

        # update invoice with details
        invoice.estimate = True
        invoice.status_detail = status_detail
        invoice.subtotal = self.membership_type.price
        invoice.total = self.membership_type.price
        invoice.balance = self.membership_type.price

        invoice.due_date = datetime.now() # TODO: change model field to null=True
        invoice.ship_date = datetime.now()  # TODO: change model field to null=True

        invoice.save()

        self.invoice = invoice
        self.save()

        return invoice

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

    def corporate_membership_name(self):
        if self.field.field_type == 'corporate_membership_id':
            try:
                value = int(self.value)
                #from corporate_memberships.models import CorporateMembership
                from django.db import connection
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT name 
                    FROM corporate_memberships_corporatemembership 
                    WHERE id=%d  
                    LIMIT 1 """ % int(self.value))
                rows = cursor.fetchall()
                if rows: return rows[0][0]
            except:
                pass

        return None
    

# Moved from management/__init__.py to here because it breaks 
# the management commands due to the ImportError.
# assign models permissions to the admin auth group
def assign_permissions(app, created_models, verbosity, **kwargs):
    from perms.utils import update_admin_group_perms
    update_admin_group_perms()
from django.db.models.signals import post_syncdb
#from memberships import models as membership_models
post_syncdb.connect(assign_permissions, sender=__file__)
