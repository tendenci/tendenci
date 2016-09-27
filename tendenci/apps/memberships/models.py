import os
import hashlib
import uuid
import time
from copy import deepcopy
from functools import partial
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models.query_utils import Q
from django.template import Context, Template
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django import forms
from importlib import import_module
from django.utils.safestring import mark_safe
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models.fields import AutoField

from tendenci.apps.base.utils import day_validate, is_blank, tcurrency
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.utils import get_notice_recipients
from tendenci.apps.base.fields import DictField, CountrySelectField
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.user_groups.models import Group
from tendenci.apps.emails.models import Email
from tendenci.apps.memberships.managers import MembershipTypeManager, \
    MembershipDefaultManager, MembershipAppManager
from tendenci.apps.base.utils import fieldify
from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.payments.models import PaymentMethod
from tendenci.apps.user_groups.models import GroupMembership
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.profiles.models import Profile
from tendenci.apps.files.models import File
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.notifications import models as notification
from tendenci.apps.directories.models import Directory
from tendenci.apps.industries.models import Industry
from tendenci.apps.regions.models import Region
from tendenci.apps.base.utils import UnicodeWriter

# from south.modelsinspector import add_introspection_rules
# add_introspection_rules([], ["^tinymce.models.HTMLField"])
# add_introspection_rules([], ["^tendenci.apps.base.fields.SlugField"])

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
FIELD_FUNCTIONS = (
    ("Group", _("Subscribe to Group")),
)
FIELD_MAX_LENGTH = 2000

VALID_MEMBERSHIP_STATUS_DETAIL = ['active', 'pending', 'expired', 'archive', 'disapproved']


class MembershipType(OrderingBaseModel, TendenciBaseModel):
    PRICE_FORMAT = u'%s - %s'
    ADMIN_FEE_FORMAT = u' (+%s admin fee)'
    RENEW_FORMAT = u' Renewal'

    guid = models.CharField(max_length=50)
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.CharField(_('Description'), max_length=500)
    price = models.DecimalField(
        _('Price'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        default=0,
        help_text=_("Set 0 for free membership.")
    )
    renewal_price = models.DecimalField(_('Renewal Price'), max_digits=15, decimal_places=2,
        blank=True, default=0, null=True, help_text=_("Set 0 for free membership."))
    # for first time processing
    admin_fee = models.DecimalField(_('Admin Fee'),
        max_digits=15, decimal_places=2, blank=True, default=0, null=True,
        help_text=_("Admin fee for the first time processing"))

    group = models.ForeignKey(Group, related_name="membership_types",
        help_text=_("Members joined will be added to this group"))

    require_approval = models.BooleanField(_('Require Approval'), default=True)
    require_payment_approval = models.BooleanField(
        _('Auto-approval requires payment'), default=True,
        help_text=_('If checked, auto-approved memberships will require a successful online payment to be auto-approved.'))
    allow_renewal = models.BooleanField(_('Allow Renewal'), default=True)
    renewal = models.BooleanField(_('Renewal Only'), default=False)
    renewal_require_approval = models.BooleanField(_('Renewal Requires Approval'), default=True)

    admin_only = models.BooleanField(_('Admin Only'), default=False)  # from allowuseroption

    never_expires = models.BooleanField(_("Never Expires"), default=False,
                                        help_text=_('If selected, skip the Renewal Options.'))
    period = models.IntegerField(_('Period'), default=0)
    period_unit = models.CharField(choices=PERIOD_UNIT_CHOICES, max_length=10)
    period_type = models.CharField(_("Period Type"), default='rolling', choices=PERIOD_CHOICES, max_length=10)

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

    fixed_option2_can_rollover = models.BooleanField(_("Allow Rollover"), default=False)
    fixed_option2_rollover_days = models.IntegerField(default=0,
            help_text=_("Membership signups after this date covers the following calendar year as well."))

    renewal_period_start = models.IntegerField(_('Renewal Period Start'), default=30,
            help_text=_("How long (in days) before the memberships expires can the member renew their membership."))
    renewal_period_end = models.IntegerField(_('Renewal Period End'), default=30,
            help_text=_("How long (in days) after the memberships expires can the member renew their membership."))
    expiration_grace_period = models.IntegerField(_('Expiration Grace Period'), default=0,
            help_text=_("The number of days after the membership expires their membership is still active."))

    objects = MembershipTypeManager()

    class Meta:
        verbose_name = _("Membership Type")
        permissions = (("view_membershiptype", _("Can view membership type")),)
        app_label = 'memberships'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Save GUID if GUID is not set.
        Save MembershipType instance.
        """
        self.guid = self.guid or uuid.uuid1().get_hex()
        super(MembershipType, self).save(*args, **kwargs)

    def get_expiration_dt(self, renewal=False, join_dt=None, renew_dt=None, previous_expire_dt=None):
        """
        Calculate the expiration date - for join or renew (renewal=True)

        Examples:

            For join:
            expiration_dt = membership_type.get_expiration_dt(join_dt=membership.join_dt)

            For renew:
            expiration_dt = membership_type.get_expiration_dt(renewal=True,
                                                              join_dt=membership.join_dt,
                                                              renew_dt=membership.renew_dt,
                                                              previous_expire_dt=None)
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

            else:  # if self.period_unit == 'years':
                if not renewal:
                    if self.rolling_option == '0':
                        # expires on end of full period
                        return join_dt + relativedelta(years=self.period)
                    else:  # self.expiration_method == '1':
                        # expires on ? days at signup (join) month
                        if not self.rolling_option1_day:
                            self.rolling_option1_day = 1
                        expiration_dt = join_dt + relativedelta(years=self.period)
                        self.rolling_option1_day = day_validate(datetime(expiration_dt.year, join_dt.month, 1),
                                                                    self.rolling_option1_day)

                        return datetime(expiration_dt.year, join_dt.month,
                            self.rolling_option1_day, expiration_dt.hour, expiration_dt.minute, expiration_dt.second)

                else:  # renewal = True
                    if self.rolling_renew_option == '0':
                        # expires on the end of full period
                        
                        # if they are renewing before expiration, the new expiration date 
                        # should start from the previous expiration date instead of the renew date
                        if isinstance(previous_expire_dt, datetime):
                            if previous_expire_dt > now:
                                return previous_expire_dt + relativedelta(years=self.period)
                            
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

                        return datetime(expiration_dt.year, renew_dt.month, self.rolling_renew_option2_day, expiration_dt.hour,
                            expiration_dt.minute, expiration_dt.second)

        else:  # self.period_type == 'fixed':
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

                self.fixed_option1_day = day_validate(datetime(self.fixed_option1_year,
                    self.fixed_option1_month, 1), self.fixed_option1_day)

                return datetime(self.fixed_option1_year, self.fixed_option1_month,
                    self.fixed_option1_day)

            else:  # self.fixed_option == '1'
                # expired on the fixed day, fixed month of current year
                if not self.fixed_option2_day:
                    self.fixed_option2_day = 1
                if not self.fixed_option2_month:
                    self.fixed_option2_month = 1
                if self.fixed_option2_month > 12:
                    self.fixed_option2_month = 12

                self.fixed_option2_day = day_validate(datetime(now.year,
                    self.fixed_option2_month, 1), self.fixed_option2_day)

                expiration_dt = datetime(now.year, self.fixed_option2_month,
                                        self.fixed_option2_day)
                if self.fixed_option2_can_rollover:
                    if not self.fixed_option2_rollover_days:
                        self.fixed_option2_rollover_days = 0
                    if (expiration_dt - now).days <= self.fixed_option2_rollover_days:
                        expiration_dt = expiration_dt + relativedelta(years=1)

                return expiration_dt

    def get_price_display(self, customer, corp_membership=None):
        renew_mode = False
        if isinstance(customer, User):
            m_list = MembershipDefault.objects.filter(user=customer, membership_type=self)
            renew_mode = any([m.can_renew() for m in m_list])

        self.renewal_price = self.renewal_price or 0
        renewal_price = self.renewal_price
        price = self.price
        above_cap_format = ''
        
        if corp_membership:
            apply_above_cap, above_cap_price = \
                    corp_membership.get_above_cap_price()
            if apply_above_cap:
                if renew_mode:
                    renewal_price = above_cap_price
                else:
                    price = above_cap_price
                above_cap_format = " (above cap price)"

        if renew_mode:
            price_display = (self.PRICE_FORMAT + self.RENEW_FORMAT) % (
                self.name,
                tcurrency(renewal_price)
            )
        else:
            if self.admin_fee:
                price_display = (self.PRICE_FORMAT + self.ADMIN_FEE_FORMAT) % (
                    self.name,
                    tcurrency(price),
                    tcurrency(self.admin_fee)
                )
            else:
                price_display = (self.PRICE_FORMAT) % (
                    self.name,
                    tcurrency(price)
                )

        if above_cap_format:
            price_display = price_display + above_cap_format

        return mark_safe(price_display)

class MembershipSet(models.Model):
    invoice = models.ForeignKey(Invoice)

    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        app_label = 'memberships'

    @property
    def group(self):
        return self.memberships()[0].group

    @property
    def membership_type(self):
        return ', '.join(self.memberships().values_list('membership_type__name', flat=True))

    @property
    def payment_method(self):
        return ', '.join(self.memberships().values_list('payment_method__human_name', flat=True))

    def memberships(self):
        return MembershipDefault.objects.filter(membership_set=self).order_by('create_dt')

    def save_invoice(self, memberships, app=None):
        invoice = Invoice()
        invoice.title = "Membership Invoice"
        invoice.estimate = True
        invoice.status_detail = "estimate"

        invoice.bill_to_user(memberships[0].user)
        invoice.ship_to_user(memberships[0].user)
        invoice.set_creator(memberships[0].user)
        invoice.set_owner(memberships[0].user)

        # price information ----------
        price = 0
        for membership in memberships:
            price += membership.get_price()

        tax = 0
        if app and app.include_tax:
            invoice.tax_rate = app.tax_rate
            tax = app.tax_rate * price
            invoice.tax = tax

        invoice.subtotal = price
        invoice.total = price + tax
        invoice.balance = price + tax

        invoice.due_date = datetime.now()
        invoice.ship_date = datetime.now()

        invoice.save()
        self.invoice = invoice
        self.save()

        self.invoice.object_type = ContentType.objects.get(
            app_label=self._meta.app_label, model=self._meta.model_name)

        self.invoice.object_id = self.pk
        self.invoice.save()

        return self.invoice

    def is_paid_online(self):
        for membership in self.membershipdefault_set.all():
            if membership.is_paid_online():
                return True
        return False

    def auto_update_paid_object(self, request, payment):
        """
        Update all membership status and dates in the set. Created archives if
        necessary.  Send out notices.  Log approval event.
        """
        for membership in self.membershipdefault_set.all():
            membership.auto_update_paid_object(request, payment)

    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        """
        id_list = []
        description = ''

        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        for i, membership in enumerate(self.membershipdefault_set.order_by('-pk')):
            id_list.append("#%d" % membership.id)

            if i == 0:
                if membership.renewal:
                    description = '%s Invoice %d for Online Membership Renewal Application - Submission ' % (
                        site_display_name,
                        inv.id,
                    )
                else:
                    description = '%s Invoice %d for Online Membership Application - Submission ' % (
                        site_display_name,
                        inv.id,
                    )

        description += ', '.join(id_list)

        return description


class MembershipDefault(TendenciBaseModel):
    """
    This membership model represents the Tendenci 4
    schema and is temporarily being used to collect
    data into a default flat membership record.
    """
    guid = models.CharField(max_length=50, editable=False)
    lang = models.CharField(max_length=10, editable=False, default='eng')
    member_number = models.CharField(max_length=50, blank=True)
    membership_type = models.ForeignKey(MembershipType)
    user = models.ForeignKey(User, editable=False)
    renewal = models.BooleanField(blank=True, default=False)
    renew_from_id = models.IntegerField(blank=True, null=True)
    certifications = models.CharField(max_length=500, blank=True)
    work_experience = models.TextField(blank=True)
    referer_url = models.CharField(max_length=500, blank=True, editable=False)
    referral_source = models.CharField(max_length=150, blank=True)
    referral_source_other = models.CharField(max_length=150, blank=True)
    referral_source_member_name = models.CharField(max_length=50, blank=True, default=u'')
    referral_source_member_number = models.CharField(max_length=50, blank=True, default=u'')
    affiliation_member_number = models.CharField(max_length=50, blank=True)
    join_dt = models.DateTimeField(_('Join Date'), blank=True, null=True)
    expire_dt = models.DateTimeField(_('Expire Date'), blank=True, null=True)
    renew_dt = models.DateTimeField(_('Renew Date'), blank=True, null=True)
    primary_practice = models.CharField(max_length=100, blank=True, default=u'')
    how_long_in_practice = models.CharField(max_length=50, blank=True, default=u'')
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    newsletter_type = models.CharField(max_length=50, blank=True)
    directory_type = models.CharField(max_length=50, blank=True)

    # workflow fields ------------------------------------------
    application_abandoned = models.BooleanField(default=False)
    application_abandoned_dt = models.DateTimeField(null=True, default=None)
    application_abandoned_user = models.ForeignKey(
        User, related_name='application_abandond_set', null=True)

    application_complete = models.BooleanField(default=True)
    application_complete_dt = models.DateTimeField(null=True, default=None)
    application_complete_user = models.ForeignKey(
        User, related_name='application_complete_set', null=True)

    application_approved = models.BooleanField(default=False)
    application_approved_dt = models.DateTimeField(null=True, default=None)
    application_approved_user = models.ForeignKey(
        User, related_name='application_approved_set', null=True)

    application_approved_denied_dt = models.DateTimeField(null=True, default=None)
    application_approved_denied_user = models.ForeignKey(
        User, related_name='application_approved_denied_set', null=True)

    application_denied = models.BooleanField(default=False)

    action_taken = models.CharField(max_length=500, blank=True)
    action_taken_dt = models.DateTimeField(null=True, default=None)
    action_taken_user = models.ForeignKey(
        User, related_name='action_taken_set', null=True)
    # workflow fields -----------------------------------------

    bod_dt = models.DateTimeField(null=True)
    personnel_notified_dt = models.DateTimeField(null=True)
    payment_received_dt = models.DateTimeField(null=True)
    payment_method = models.ForeignKey(PaymentMethod, null=True)
    override = models.BooleanField(default=False)
    override_price = models.FloatField(null=True)
    exported = models.BooleanField(default=False)
    chapter = models.CharField(max_length=150, blank=True)
    areas_of_expertise = models.CharField(max_length=1000, blank=True)
    corp_profile_id = models.IntegerField(blank=True, default=0)
    corporate_membership_id = models.IntegerField(
        _('Corporate Membership'), blank=True, null=True)
    home_state = models.CharField(max_length=50, blank=True, default=u'')
    year_left_native_country = models.IntegerField(blank=True, null=True)
    network_sectors = models.CharField(max_length=250, blank=True, default=u'')
    networking = models.CharField(max_length=250, blank=True, default=u'')
    government_worker = models.BooleanField(default=False)
    government_agency = models.CharField(max_length=250, blank=True, default=u'')
    license_number = models.CharField(max_length=50, blank=True, default=u'')
    license_state = models.CharField(max_length=50, blank=True, default=u'')
    industry = models.ForeignKey(Industry, blank=True, null=True)
    region = models.ForeignKey(Region, blank=True, null=True)
    company_size = models.CharField(max_length=50, blank=True, default=u'')
    promotion_code = models.CharField(max_length=50, blank=True, default=u'')
    directory = models.ForeignKey(Directory, blank=True, null=True)
    groups = models.ManyToManyField(Group)

    membership_set = models.ForeignKey(MembershipSet, blank=True, null=True)
    app = models.ForeignKey("MembershipApp", null=True, on_delete=models.SET_NULL)

    objects = MembershipDefaultManager()

    class Meta:
        verbose_name = _(u'Membership')
        verbose_name_plural = _(u'Memberships')
        permissions = (("approve_membershipdefault", _("Can approve memberships")),)
        app_label = 'memberships'

    def __unicode__(self):
        """
        Returns summary of membership object
        """
        u = "Membership object"
        if self.pk:
            u = "Membership %d for %s" % (self.pk, self.user.get_full_name())

        return u

    @models.permalink
    def get_absolute_url(self):
        """
        Returns admin change_form page.
        """
        return ('membership.details', [self.pk])
        # return ('admin:memberships_membershipdefault_change', [self.pk])

    @models.permalink
    def get_current_membership_url(self):
        """
        Returns link to url of the most current membership.
        """
        memberships = self.user.membershipdefault_set.filter(membership_type=self.membership_type).order_by('-id')

        return ('membership.details', [memberships[0].pk])

    @property
    def group(self):
        return self.membership_type.group

    def save(self, *args, **kwargs):
        """
        Set GUID if not already set.
        """
        self.guid = self.guid or uuid.uuid1().get_hex()
        # set the status_detail to pending if not specified
        # the default 'active' is causing problems
        if not self.status_detail:
            self.status_detail = 'pending'
        super(MembershipDefault, self).save(*args, **kwargs)

    @property
    def demographics(self):
        """
        Binds demographic-table which holds
        user-defined information.
        """
        if hasattr(self, 'user') and self.user:
            if hasattr(self.user, 'demographics'):
                return self.user.demographics
    
    @property
    def obj_status(self):
        t = '<span class="t-profile-status t-status-%s">%s</span>'

        if self.status:
            if self.status_detail == 'paid - pending approval':
                value = t % ('pending', self.status_detail.capitalize())
            else:
                value = t % (self.status_detail, self.status_detail.capitalize())
        else:
            value = t % ('inactive','Inactive')

        return mark_safe(value)

    def demographic_sort_key(self, field_name):
        """
        Returns the key to sort on when
        using the list.sort method.
        """
        digit = field_name.replace('ud', u'')
        return int(digit) if digit.isdigit() else 0

    def get_demographics(self):
        """
        Returns a list of 2-tuples (field name, field value)
        """
        if not self.demographics:
            return []  # empty list

        demographic = self.demographics

        field_names = demographic._meta.get_all_field_names()
        field_names.sort(key=self.demographic_sort_key)  # sort by ud number

        field_dict = {}

        if self.app:
            for field in self.app.fields.all():
                field_dict[field.field_name] = field.label

        field_list = []
        for field_name in field_names:
            if field_name.startswith('ud'):
                field_label = field_dict.get(field_name, field_name)
                if hasattr(demographic, field_name):  # catches broken db relationships
                    data = getattr(demographic, field_name)
                    try:
                        is_file = eval(data).get('type') == u'file'
                    except Exception as e:
                        is_file = False

                    if is_file:
                        field_list.append((field_label, eval(data).get('html')))
                    else:
                        field_list.append((field_label, data))

        if is_blank(dict(field_list).values()):
            return []  # empty list

        return field_list

    def get_app(self):
        if not self.app:
            apps = MembershipApp.objects.filter(
                           status=True,
                           status_detail__in=['active', 'published'],
                           membership_types__in=[self.membership_type]
                           ).order_by('id')
            if self.corporate_membership_id:
                apps = apps.filter(use_for_corp=True)
            else:
                apps = apps.filter(use_for_corp=False)
            if apps:
                self.app = apps[0]
                self.save()

    def get_archived_memberships(self):
        """
        Returns back a list of archived memberships
        in order of newest to oldest
        """
        memberships = self.user.membershipdefault_set.filter(
            status_detail='archive', membership_type=self.membership_type).order_by('join_dt')

        return memberships

    @classmethod
    def refresh_groups(cls):
        """
        Adds or Removes users from groups
        depending on their membership status_detail.
        """
        for membership_type in MembershipType.objects.all():
            for user in User.objects.all():

                status_details = MembershipDefault.objects.filter(
                    user=user,
                    membership_type=membership_type,
                    status=True,
                    status_detail__in=['active', 'pending', 'expired'],
                ).values_list('status_detail', flat=True)

                status_details = list(status_details)
                if status_details.count('active') > 1:
                    memberships = MembershipDefault.objects.filter(
                        user=user,
                        membership_type=membership_type,
                        status=True,
                        status_detail='active'
                    ).order_by('-pk')[1:]

                    for membership in memberships:
                        membership.status_detail = 'archive'
                        membership.save()

                if 'active' in status_details:

                    exists = GroupMembership.objects.filter(
                        member=user,
                        group=membership_type.group,
                    ).exists()

                    if not exists:
                        GroupMembership.add_to_group(
                            member=user,
                            group=membership_type.group,
                        )
                else:
                    # remove from group
                    GroupMembership.objects.filter(
                        member=user,
                        group=membership_type.group,
                    ).delete()

    @classmethod
    def QS_ACTIVE(cls):
        """
        Returns memberships of status_detail='active'
        """
        return MembershipDefault.objects.filter(status_detail__iexact='active')

    @classmethod
    def QS_PENDING(cls):
        """
        Returns memberships of status_detail='pending'
        """
        return MembershipDefault.objects.filter(status_detail__iexact='pending')

    def get_corporate_profile(self):
        """
        Returns corporate profile object
        else returns None type object.
        """
        from tendenci.apps.corporate_memberships.models import CorpProfile
        [corporate_profile] = CorpProfile.objects.filter(
            pk=self.corp_profile_id) or [None]

        return corporate_profile

    def get_corporate_membership(self):
        """
        Returns corporate membership object
        else returns None type object.
        """
        from tendenci.apps.corporate_memberships.models import CorpMembership
        [corporate_membership] = CorpMembership.objects.filter(
            pk=self.corporate_membership_id) or [None]

        return corporate_membership

    def send_email(self, request, notice_type):
        """
        Convenience method for sending
            typical membership emails.
        Returns outcome via boolean.
        """
        ret = Notice.send_notice(
            request=request,
            emails=self.user.email,
            notice_type=notice_type,
            membership=self,
            membership_type=self.membership_type,
        )
        # log notice
        Notice.log_notices([self],
                           notice_type=notice_type
                           )

        return ret

    def email_corp_reps(self, request):
        """
        Notify corp reps when individuals joined/renewed under a corporation.
        """
        if self.corporate_membership_id:
            from tendenci.apps.corporate_memberships.models import CorpMembership
            [corp_membership] = CorpMembership.objects.filter(
                                pk=self.corporate_membership_id
                                )[:1] or [None]
            if corp_membership:
                reps = corp_membership.corp_profile.reps.all()
                params = {
                        'corp_membership': corp_membership,
                        'membership': self
                          }
                for rep in reps:
                    params.update({'user': rep.user})
                    subject = render_to_string(
                        'memberships/notices/email_corp_reps_subject.html',
                        params,
                        context_instance=RequestContext(request))
                    subject = subject.strip('\n').strip('\r')
                    body = render_to_string(
                                'memberships/notices/email_corp_reps_body.html',
                                params,
                                context_instance=RequestContext(request))

                    email = Email(recipient=rep.user.email,
                                  subject=subject,
                                  body=body)
                    email.send()

    def approve(self, request_user=AnonymousUser()):
        """
        Approve this membership.
            - Assert user is in group.
            - Create new invoice.
            - Archive old memberships [of same type].
            - Show member number on profile.

        Will not approve:
            - Active memberships
            - Expired memberships
            - Archived memberships
        """

        good = (
            not self.is_expired(),
            not self.is_archived(),
        )

        if not all(good):
            return False

        NOW = datetime.now()

        self.status = True
        self.status_detail = 'active'

        # application approved ---------------
        self.application_approved = True
        self.application_approved_dt = \
            self.application_approved_dt or NOW

        if request_user and request_user.is_authenticated():  # else: don't set
            self.application_approved_user = request_user
            self.application_approved_denied_user = request_user
            self.action_taken_user = request_user

        # application approved/denied ---------------
        self.application_approved_denied_dt = \
            self.application_approved_denied_dt or NOW

        # action_taken ------------------------------
        self.action_taken = True
        self.action_taken_dt = self.action_taken_dt or NOW

        self.set_join_dt()
        self.set_renew_dt()
        self.set_expire_dt()
        self.set_member_number()
        self.save()

        # user in [membership] group
        self.group_refresh()

        # new invoice; bound via ct and object_id
        self.save_invoice(status_detail='tendered')

        # archive other membership [of this type]
        self.archive_old_memberships()

        # show member number on profile
        self.user.profile.refresh_member_number()

        # Activate user
        if not self.user.is_active:
            from tendenci.apps.notifications.utils import send_welcome_email
            self.user.is_active = True
            self.user.save()
            send_welcome_email(self.user)

        return self

    def renew(self, request_user):
        """
        Renew this membership.
            - Assert user is in group.
            - Create new invoice.
            - Archive old memberships [of same type].
            - Show member number on profile.
        """
        NOW = datetime.now()

        if self.is_pending():
            dupe = self
        elif any((self.is_active(), self.is_expired())):
            dupe = deepcopy(self)
            dupe.pk = None  # disconnect from db record
        else:
            return False

        dupe.status = True,
        dupe.status_detail = 'active'
        
        dupe.renewal = True
        if not dupe is self:
            dupe.renew_from_id = self.id

        # application approved ---------------
        dupe.application_approved = True
        dupe.application_approved_dt = NOW

        if request_user and not request_user.is_anonymous():  # else: don't set
            dupe.application_approved_user = request_user
            dupe.application_approved_denied_user = request_user
            dupe.action_taken_user = request_user

        # application approved/denied ---------------
        dupe.application_approved_denied_dt = NOW

        # action_taken ------------------------------
        dupe.action_taken = True
        dupe.action_taken_dt = NOW

        dupe.save()
        dupe.set_join_dt()
        dupe.set_renew_dt()
        dupe.set_expire_dt()
        dupe.save()

        # add to [membership] group
        dupe.membership_type.group.add_user(self.user)

        # new invoice; bound via ct and object_id
        dupe.save_invoice(status_detail='tendered')

        # archive other membership [of this type]
        dupe.archive_old_memberships()

        # show member number on profile
        dupe.user.profile.refresh_member_number()

        return dupe

    def disapprove(self, request_user=None):
        """
        Disapprove this membership.

        Will not disapprove:
            - Archived memberships
            - Expired memberships (instead: you should renew it)
        """
        good = (
            not self.is_expired(),
            self.status_detail != 'archive',
        )

        if not all(good):
            return False

        NOW = datetime.now()

        self.status = True,
        self.status_detail = 'disapproved'

        # application approved/denied ---------------
        self.application_denied = True
        self.application_approved_denied_dt = \
            self.application_approved_denied_dt or NOW
        if request_user:  # else: don't set
            self.application_approved_denied_user = request_user

        # action_taken ------------------------------
        self.action_taken = True
        self.action_taken_dt = self.action_taken_dt or NOW
        if request_user:  # else: don't set
            self.action_taken_user = request_user

        self.save()

        # user in [membership] group
        self.group_refresh()

        # new invoice; bound via ct and object_id
        self.save_invoice(status_detail='tendered')

        # archive other membership [of this type]
        self.archive_old_memberships()

        # show member number on profile
        self.user.profile.refresh_member_number()

        return True

    def expire(self, request_user):
        """
        Expire this membership.
            - Set status_detail to 'expired'
            - Remove grom group.
            - Remove profile member number.

        Will only expire approved memberships.
        """

        if self.is_approved() or (self.is_expired() and self.status_detail == 'active'):
            NOW = datetime.now()
    
            self.status = True
            self.status_detail = 'expired'
    
            # action_taken ------------------------------
            self.action_taken = True
            self.action_taken_dt = self.action_taken_dt or NOW
            if request_user:  # else: don't set
                self.action_taken_user = request_user
    
            self.save()
    
            # remove from group
            self.group_refresh()
    
            # show member number on profile
            self.user.profile.refresh_member_number()
    
            return True
        
        return False

    def pend(self):
        """
        Set the membership to pending.
        This should not be a method available
        to the end-user.  Used within membership process.
        """
        if self.status_detail == 'archive':
            return False

        self.status = True,
        self.status_detail = 'pending'

        # application approved ---------------
        self.application_approved = False
        self.application_approved_dt = None
        self.application_approved_user = None

        # application approved/denied ---------------
        self.application_approved_denied_dt = None
        self.application_approved_denied_user = None

        # action_taken ------------------------------
        self.action_taken = False
        self.action_taken_dt = None
        self.action_taken_user = None

        self.set_join_dt()
        self.set_renew_dt()
        self.set_expire_dt()

        # add to [membership] group
        self.group_refresh()

        # new invoice; bound via ct and object_id
        self.save_invoice(status_detail='estimate')

        # remove member number on profile
        self.user.profile.refresh_member_number()

        return True

    def is_forever(self):
        """
        Returns boolean.
        Tests if expiration datetime exists.
        """
        return not self.expire_dt

    def get_expire_dt(self):
        """
        Returns None type object
        or datetime object
        """
        grace_period = self.membership_type.expiration_grace_period

        if not self.expire_dt:
            return None

        return self.expire_dt + relativedelta(days=grace_period)

    def is_expired(self):
        """
        status=True, status_detail='active' or 'expired',
        out of the grace period.
        """
        if self.status and self.status_detail.lower() in ('active', 'expired'):
            if self.expire_dt:
                return self.expire_dt <= datetime.now() and \
                    (not self.in_grace_period())
        return False

    def is_pending(self):
        """
        Return boolean; The memberships pending state.
        """
        if self.status and self.status_detail == 'pending':
            return True
        return False

    def is_active(self):
        """
        status = True, status_detail = 'active', and has not expired
        considers grace period when evaluating expiration date-time
        """
        return self.status and self.status_detail.lower() == 'active'

    def is_approved(self):
        """
        self.is_active()
        self.application_approved
        """
        if self.is_active():

            # membership does not expire
            if self.is_forever():
                return True

            # membership has not expired
            if not self.is_expired():
                return True

        return False

    def is_archived(self):
        """
        self.is_active()
        self.status_detail = 'archive'
        """
        return self.status and self.status_detail.lower() == 'archive'

    def get_status(self):
        """
        Returns status of membership
        'pending', 'active', 'disapproved', 'expired', 'archive'
        """
        return self.status_detail.lower()

    def copy(self):
        """
        Return a copy of the membership object
        """
        membership = MembershipDefault()

        ignore_fields = [
            'id',
            'renewal',
            'renew_dt',
            'status',
            'status_detail',
            'application_approved',
            'application_approved_dt',
            'application_approved_user',
            'application_approved_denied_dt',
            'application_approved_denied_user',
            'application_denied'
        ]

        field_names = [
            field.name
            for field in self.__class__._meta.fields
            if field.name not in ignore_fields
        ]

        for name in field_names:
            if hasattr(self, name):
                setattr(membership, name, getattr(self, name))
        return membership

    def archive_old_memberships(self):
        """
        Archive old memberships that are active, pending, and expired
        and of the same membership type.  Making sure not to
        archive the newest membership.
        """
        memberships = self.qs_memberships()
        for membership in memberships:

            if membership != self:
                membership.status_detail = 'archive'
                membership.save()

        # if they renewed from a different membership type
        # renew_from_id should not be id, but just in case
        if self.renew_from_id and self.renew_from_id != self.id:
            [membership_from] = MembershipDefault.objects.filter(
                                id=self.renew_from_id).exclude(
                                status_detail='archive'
                                )[:1] or [None]
            if membership_from:
                membership_from.status_detail = 'archive'
                membership_from.save()
                

    def approval_required(self):
        """
        Returns a boolean value on whether approval is required
        This is dependent on whether membership is a join or renewal.
        """
        if self.renewal:
            if not self.membership_type.renewal_require_approval:
                if not self.membership_type.require_payment_approval \
                  or self.get_invoice().balance <= 0:
                    # auto approve if not require approval or paid or free
                    return False
        else: # join
            if not self.membership_type.require_approval:
                if not self.membership_type.require_payment_approval \
                  or self.get_invoice().balance <= 0:
                    return False
        return True

    def group_refresh(self):
        """
        Look at the memberships status and decide
        whether the user should or should not be in
        the group.
        """

        active = (self.status == True, self.status_detail.lower() == 'active')

        if all(active):  # should be in group; make sure they're in
            self.membership_type.group.add_user(self.user)

            # add user to groups selected by user
            groups = self.groups.all()

            for group in groups:
                if not group.is_member(self.user):
                    group.add_user(self.user)

        else:  # should not be in group; make sure they're out
            GroupMembership.objects.filter(
                member=self.user,
                group=self.membership_type.group
            ).delete()

    def get_or_create_user(self, **kwargs):
        """
        Return a user that's newly created or already existed.
        Return new or existing user.

        If username is passed.  It uses the username to return
        an existing user record or creates a new user record.

        If a password is passed; it is only used in order to
        create a new user account.
        """
        from tendenci.apps.memberships.utils import spawn_username

        un = kwargs.get('username', u'')
        pw = kwargs.get('password', u'')
        fn = kwargs.get('first_name', u'')
        ln = kwargs.get('last_name', u'')
        em = kwargs.get('email', u'')

        user = None
        created = False

        # get user -------------
        if hasattr(self, 'user'):
            user = self.user
        elif un:
            # created = False
            [user] = User.objects.filter(
                username=un)[:1] or [None]
        elif em:
            [user] = User.objects.filter(
                email=em).order_by('-pk')[:1] or [None]

        if not user:
            created = True
            user = User.objects.create_user(**{
                'username': un or spawn_username(fn[:1], ln),
                'email': em,
                'password': pw or hashlib.sha1(em).hexdigest()[:6],
            })

            user.first_name = fn
            user.last_name = ln
            user.save()

            Profile.objects.create_profile(user)

        return user, created

    def in_grace_period(self):
        """ Returns True if a member's expiration date has passed but status detail is still active.
        """
        expire_with_grace_period_dt = self.get_expire_dt()

        if not expire_with_grace_period_dt:
            return False

        return all([
            self.expire_dt < datetime.now(),
            expire_with_grace_period_dt > datetime.now(),
            self.status_detail == "active"])

    def get_renewal_period_dt(self):
        """
         Returns a none type object or 2-tuple with start_dt and end_dt
        """
        if not self.membership_type.allow_renewal:
            return None

        if not isinstance(self.expire_dt, datetime):
            return None  # membership does not expire

        start_dt = self.expire_dt - timedelta(
            days=self.membership_type.renewal_period_start
        )

        # the end_dt should be the end of the end_dt not start of the end_dt
        # not datetime.datetime(2013, 2, 21, 0, 0),
        # but datetime.datetime(2013, 2, 21, 23, 59, 59)
        end_dt = self.get_renewal_period_end_dt()

        return (start_dt, end_dt)

    def get_renewal_period_end_dt(self):
        return self.expire_dt + timedelta(
            days=self.membership_type.renewal_period_end + 1
        ) - timedelta(seconds=1)

    def is_renewal(self):
        """
        Checks if there are active or expired memberships
        of this same membership type bound to this user
        """
        if self.renew_from_id:
            return True

        m_exists = self.user.membershipdefault_set.filter(
                    Q(status_detail='active') | Q(status_detail='expired'))
        
        if MembershipApp.objects.filter(allow_multiple_membership=True).exists(): 
            m_exists = m_exists.filter(
                membership_type=self.membership_type)
        m_exists = m_exists.exists()
        
        return m_exists

    def can_renew(self):
        """
        Checks if ...
        membership.is_forever() i.e. never ends
        membership type allows renewals
        membership renewal period was specified
        membership is within renewal period

        returns boolean
        """
        renewal_period = self.get_renewal_period_dt()

        # renewal not allowed; or no renewal period
        if not renewal_period:
            return False

        # can only renew from active or expired
        if not self.get_status() in ['active', 'expired']:
            return False

        # assert that we're within the renewal period
        start_dt, end_dt = renewal_period
        return (datetime.now() >= start_dt and datetime.now() <= end_dt)

    def past_renewal(self):
        """
        Check if the membership is past renewal.
        Returns boolean value.
        """
        renewal_period = self.get_renewal_period_dt()

        # renewal not allowed; or no renewal period
        if not renewal_period:
            return False

        # can only renew from approved state
        if not self.get_status() in ['active', 'expired']:
            return False

        # assert that we're within the renewal period
        end_dt = renewal_period[1]

        return datetime.now() > end_dt

    def get_since_dt(self):
        memberships = MembershipDefault.objects.filter(
            user=self.user,
            status=True,
            join_dt__isnull=False
        ).order_by('pk')

        return memberships[0].join_dt if memberships else self.create_dt

    def get_actions(self, **kwargs):
        """
        Returns dictionary of actions (key) with label (value)

        Possible actions:
            approve
            disapprove
            make pending
            archive
        """
        from collections import OrderedDict
        actions = OrderedDict()
        status = self.get_status()

        is_superuser = kwargs.get('is_superuser', False)

        form_link = u''
        if self.app:
            form_link = '%s?username=%s&membership_type=%s' % (
                reverse('membership_default.renew', kwargs={'slug': self.app.slug, 'membership_id': self.id}),
                self.user.username,
                self.membership_type.pk)

        approve_link = '%s?approve=' % reverse('membership.details', args=[self.pk])
        disapprove_link = '%s?disapprove' % reverse('membership.details', args=[self.pk])
        expire_link = '%s?expire' % reverse('membership.details', args=[self.pk])

        if self.can_renew() and form_link:
            renew = {form_link: u'Renew Membership'}
        elif is_superuser and form_link:
            renew = {form_link: u'Admin: Renew Membership'}
        else:
            renew = {}

        if status == 'active':
            actions.update(renew)
            actions.update({
                # '?action=pend': u'Make Pending',
                expire_link: u'Expire Membership'})
        elif status == 'disapproved':
            pass
            # actions.update({
                # '?action=pend': u'Make Pending',
                # expire_link: u'Expire Membership'})
        elif status == 'pending':
            actions.update({
                approve_link: u'Approve',
                disapprove_link: u'Disapprove',
                expire_link: u'Expire Membership'})
        elif status == 'expired':
            actions.update({
                approve_link: u'Approve Membership'})

        return actions

    def get_invoice(self):
        """
        Get invoice object.  The invoice object is not
        associated via ForeignKey, it's associated via ContentType.
        """
        # Get invoice from membership set
        if self.membership_set:
            return self.membership_set.invoice

        # Check if there is an invoice bound to by content_type
        content_type = ContentType.objects.get(
            app_label=self._meta.app_label, model=self._meta.model_name)

        [invoice] = Invoice.objects.filter(
                object_type=content_type, object_id=self.pk
            )[:1] or [None]

        return invoice

    def save_invoice(self, **kwargs):
        """
        Update invoice; else create invoice.
        Pass 'status_detail' to set estimate or tendered.
        """

        creator = kwargs.get('creator')
        if not isinstance(creator, User):
            creator = self.user

        status_detail = kwargs.get('status_detail', 'estimate')

        content_type = ContentType.objects.get(
            app_label=self._meta.app_label, model=self._meta.model_name)

        invoice = self.get_invoice()

        if not invoice:
            invoice = Invoice()

        if status_detail == 'estimate':
            invoice.estimate = True
            invoice.status_detail = status_detail

        invoice.bill_to_user(self.user)
        invoice.ship_to_user(self.user)
        invoice.set_creator(creator)
        invoice.set_owner(self.user)

        # price information and bind invoice to membership ----------
        # Only set for new invoices
        if not invoice.pk:
            price = self.get_price()
            invoice.subtotal = price
            invoice.total = price
            invoice.balance = price

            invoice.object_type = content_type
            invoice.object_id = self.pk

        invoice.due_date = invoice.due_date or datetime.now()
        invoice.ship_date = invoice.ship_date or datetime.now()

        invoice.save()

        # saves invoice [as well]
        if status_detail == 'tendered':
            invoice.tender(self.user)

        return invoice

    def get_price(self):
        """
        Returns price

        Considers:
            Join price
            Renew price
            Admin Price
            Corporate price

        Admin price is only included on joins.
        Corporate price, trumps all membership prices.
        """
        if self.corporate_membership_id:
            from tendenci.apps.corporate_memberships.models import CorpMembership
            [corp_membership] = CorpMembership.objects.filter(
                                id=self.corporate_membership_id)[:1] or [None]
            if corp_membership:
                # num_exclude - exclude this membership
                apply_above_cap, above_cap_price = \
                    corp_membership.get_above_cap_price(num_exclude=1)
                if apply_above_cap:
                    if self.renewal:
                        return above_cap_price
                    else:
                        return above_cap_price + (self.membership_type.admin_fee or 0)
   
        if self.renewal:
            return self.membership_type.renewal_price or 0
        else:
            return self.membership_type.price + (self.membership_type.admin_fee or 0)

    def qs_memberships(self, **kwargs):
        """
        Get all memberships of this type for this user.
        Breaks if self.user is not set.
        """
        if MembershipApp.objects.filter(allow_multiple_membership=True).exists():
            return MembershipDefault.objects.filter(
                user=self.user,
                membership_type=self.membership_type)
        else:
            return MembershipDefault.objects.filter(
                user=self.user)

    def create_member_number(self):
        """
        Create a unique membership number using setting MemberNumberBaseNumber.
                new member number = MemberNumberBaseNumber + 1

        If the new member number has already been taken for some reason,
                new member number = maximum member number in system + 1
        """
        if self.id and not self.member_number:
            base_number = get_setting('module',
                                      'memberships',
                                      'membernumberbasenumber')
            if not isinstance(base_number, int):
                # default to 5000 if not specified
                base_number = 5000

            new_member_number = str(base_number + self.id)
            # check if this number's already been taken
            if MembershipDefault.objects.filter(
                                member_number=new_member_number
                                ).exclude(user=self.user
                                          ).exists():
                # get the maximum member_number in the system
                [m_max] = MembershipDefault.objects.extra(
                                    select={'length': 'Length(member_number)'}
                                    ).filter(
                                    member_number__regex=r'^\d+$'
                                    ).order_by('-length', '-member_number'
                                               )[:1] or [None]
                if m_max:
                    new_member_number = str(int(m_max.member_number) + 1)
                else:
                    new_member_number = str(base_number + 1)

            return new_member_number

        return ''

    def set_join_dt(self):
        """
        Looks through old memberships to discover join dt
        """

        # cannot set renew dt if approved dt
        # does not exist (DNE)
        if not self.application_approved_dt:
            return None

        # memberships with join date
        memberships = self.qs_memberships().filter(
            join_dt__isnull=False
            ).exclude(status_detail='disapproved'
            ).exclude(status_detail='pending')

        if self.pk:
            memberships = memberships.exclude(pk=self.pk)

        if memberships:
            self.join_dt = memberships[0].join_dt
        else:
            self.join_dt = self.join_dt or self.application_approved_dt

    def set_renew_dt(self):
        """
        Dependent on self.application_approved and
        self.application_approved_dt

        If qualified memberships exists for this
        Membership.user set
        Membership.renew_dt = Membership.application_approved_dt
        """

        approved = (
            self.application_approved,
            self.application_approved_dt,
        )

        # if not approved
        # set renew_dt and get out
        if not all(approved):
            self.renew_dt = None
            return None

        memberships = self.qs_memberships(
            ).exclude(status_detail='disapproved'
            ).exclude(status_detail='pending')

        if self.pk:
            memberships = memberships.exclude(pk=self.pk)

        if memberships or self.renew_from_id:
            self.renew_dt = self.application_approved_dt

    def set_expire_dt(self):
        """
        User MembershipType to set expiration dt
        """

        approved = (
            self.application_approved,
            self.application_approved_dt,
        )

        # if not approved
        # set expire_dt and get out
        if not all(approved):
            self.expire_dt = None
            return None

        if self.corporate_membership_id:
            # corp individuals expire with their corporate membership
            from tendenci.apps.corporate_memberships.models import CorpMembership
            [corp_expiration_dt] = CorpMembership.objects.filter(
                                        id=self.corporate_membership_id
                                        ).values_list('expiration_dt',
                                                      flat=True)[:1] or [None]
            self.expire_dt = corp_expiration_dt
        else:

            if self.renew_dt:
                if self.renew_from_id:
                    [previous_expire_dt] = MembershipDefault.objects.filter(
                                                id=self.renew_from_id).values_list(
                                                'expire_dt', flat=True)[:1] or [None]
                else:
                    previous_expire_dt = None
                self.expire_dt = self.membership_type.get_expiration_dt(
                    renewal=self.is_renewal(), renew_dt=self.renew_dt, previous_expire_dt=previous_expire_dt
                )
            elif self.join_dt:
                self.expire_dt = self.membership_type.get_expiration_dt(
                    renewal=self.is_renewal(), join_dt=self.join_dt
                )

    def set_member_number(self):
        """
        Sets membership number via previous
        membership record.
        """
        # if member_number; get out
        if self.member_number:
            return self.member_number

        memberships = self.qs_memberships().exclude(
            member_number__exact=u'').order_by('-pk')

        if memberships:
            self.member_number = memberships[0].member_number

        if not self.member_number:
            self.member_number = self.create_member_number()

        return self.member_number

    def is_paid_online(self):
        """
        Returns a boolean value.  Checks whether the payment
        method is online and the membership is not free.
        """
        good = (
            self.get_invoice().total > 0,
            self.payment_method and self.payment_method.is_online,
        )

        return all(good)

    def get_field_items(self):
        """
        """
        app = self.app

        items = {}
        field_names = MembershipAppField.objects.filter(
                                        membership_app=app,
                                        display=True,
                                        ).exclude(
                                        field_name=''
                                        ).values_list('field_name',
                                                      flat=True)
        if field_names:
            user = self.user
            profile = hasattr(user, 'profile') and user.profile
            if hasattr(user, 'demographics'):
                demographics = getattr(user, 'demographics')
            else:
                demographics = None
            for field_name in field_names:
                if hasattr(user, field_name):
                    items[field_name] = getattr(user, field_name)
                elif hasattr(profile, field_name):
                    items[field_name] = getattr(profile, field_name)
                elif demographics and hasattr(demographics, field_name):
                    items[field_name] = getattr(demographics, field_name)
                elif hasattr(self, field_name):
                    items[field_name] = getattr(self, field_name)

            for name, value in items.iteritems():
                if hasattr(value, 'all'):
                    items[name] = ', '.join([item.__unicode__() \
                                             for item in value.all()])

        return items

    def corpmembership(self):
        if not self.corporate_membership_id:
            return None

        from tendenci.apps.corporate_memberships.models import CorpMembership
        [corp_memb] = CorpMembership.objects.filter(
                    pk=self.corporate_membership_id)[:1] or [None]
        return corp_memb

    def membership_type_link(self):
        link = '<a href="%s">%s</a>' % (
                reverse('admin:memberships_membershiptype_change',
                        args=[self.membership_type.id]),
                        self.membership_type.name)
        if self.corporate_membership_id:
            from tendenci.apps.corporate_memberships.models import CorpMembership
            [corp_member] = CorpMembership.objects.filter(id=self.corporate_membership_id)[:1] or [None]
            if corp_member:
                link = '%s (<a href="%s">corp</a> %s)' % (
                    link,
                    reverse('corpmembership.view',
                            args=[self.corporate_membership_id]),
                    corp_member.status_detail)
        return link
    membership_type_link.allow_tags = True
    membership_type_link.short_description = u'Membership Type'

    def auto_update_paid_object(self, request, payment):
        """
        Update membership status and dates. Created archives if
        necessary.  Send out notices.  Log approval event.
        """
        from tendenci.apps.notifications.utils import send_welcome_email

        open_renewal = (
            self.is_renewal(),
            not self.membership_type.renewal_require_approval)

        open_join = (
            not self.is_renewal(),
            not self.membership_type.require_approval)

        can_approve = all(open_renewal) or all(open_join)
        can_approve = can_approve or request.user.profile.is_superuser

        if can_approve:

            self.user, created = self.get_or_create_user()
            if created:
                send_welcome_email(self.user)

            if self.is_renewal():
                # renewal returns new MembershipDefault instance
                # old MembershipDefault instance is marked status_detail = "archive"
                self = self.renew(request.user)
                Notice.send_notice(
                    request=request,
                    emails=self.user.email,
                    notice_type='renewal',
                    membership=self,
                    membership_type=self.membership_type,
                )
                EventLog.objects.log(
                    instance=self,
                    action='membership_renewed'
                )
            else:
                self.approve()
                Notice.send_notice(
                    request=request,
                    emails=self.user.email,
                    notice_type='approve',
                    membership=self,
                    membership_type=self.membership_type,
                )
                EventLog.objects.log(
                    instance=self,
                    action='membership_approved'
                )

            if self.corporate_membership_id:
                # notify corp reps
                self.email_corp_reps(request)

    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the event sale
        """
        from tendenci.apps.accountings.models import Acct, AcctEntry, AcctTran
        from tendenci.apps.accountings.utils import make_acct_entries_initial, make_acct_entries_closing

        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)

            # CREDIT event SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount * (-1))

    def get_acct_number(self, discount=False):
        # reference: /accountings/account_numbers/
        return 464700 if discount else 404700

    # def custom_fields(self):
    #     return self.membershipfield_set.order_by('field__position')


def get_import_file_path(instance, filename):
    return "imports/memberships/{uuid}/{filename}".format(
                            uuid=uuid.uuid1().get_hex()[:8],
                            filename=filename)


class MembershipImport(models.Model):
    INTERACTIVE_CHOICES = (
        (1, _('Interactive')),
        (0, _('Not Interactive (no login)')),
    )

    OVERRIDE_CHOICES = (
        (0, _('Blank Fields')),
        (1, _('All Fields (override)')),
    )

    STATUS_CHOICES = (
        ('not_started', _('Not Started')),
        ('preprocessing', _('Pre_processing')),
        ('preprocess_done', _('Pre_process Done')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
    )

#     app = models.ForeignKey('App', null=True)
    upload_file = models.FileField(_("Upload File"), max_length=260,
                                   upload_to=get_import_file_path,
                                   null=True)
    recap_file = models.FileField(_("Recap File"), max_length=260,
                                   null=True)
    # store the header line to assist in generating recap
    header_line = models.CharField(_('Header Line'), max_length=3000, default='')
    # active users
    interactive = models.IntegerField(choices=INTERACTIVE_CHOICES, default=0)
    # overwrite already existing fields if match
    override = models.IntegerField(choices=OVERRIDE_CHOICES, default=0)
    # uniqueness key
    key = models.CharField(_('Key'), max_length=50,
                           default="email/member_number/fn_ln_phone")

    total_rows = models.IntegerField(default=0)
    num_processed = models.IntegerField(default=0)
    summary = models.CharField(_('Summary'), max_length=500,
                           null=True, default='')
    status = models.CharField(choices=STATUS_CHOICES,
                              max_length=50,
                              default='not_started')
    complete_dt = models.DateTimeField(null=True)

    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'memberships'

    def get_file(self):
        if self.upload_file:
            return self.upload_file

        return File.objects.get_for_model(self)[0]

    def __unicode__(self):
        return self.get_file().file.name

    def generate_recap(self):
        if not self.recap_file and self.header_line:
            file_name = 'membership_import_%d_recap.csv' % self.id
            file_path = '%s/%s' % (os.path.split(self.upload_file.name)[0],
                                   file_name)
            f = default_storage.open(file_path, 'wb')
            recap_writer = UnicodeWriter(f, encoding='utf-8')
            header_row = self.header_line.split(',')
            if 'status' in header_row:
                header_row.remove('status')
            if 'status_detail' in header_row:
                header_row.remove('status_detail')
            header_row.extend(['action', 'error'])
            recap_writer.writerow(header_row)
            data_list = MembershipImportData.objects.filter(
                mimport=self).order_by('row_num')
            for idata in data_list:
                data_dict = idata.row_data
                row = [data_dict[k] for k in header_row if k in data_dict]
                row.extend([idata.action_taken, idata.error])
                row = [smart_str(s).decode('utf-8') for s in row]
                recap_writer.writerow(row)

            f.close()
            self.recap_file.name = file_path
            self.save()


class MembershipImportData(models.Model):
    mimport = models.ForeignKey(MembershipImport, related_name="membership_import_data")
    # dictionary object representing a row in csv
    row_data = DictField(_('Row Data'))
    # the original row number in the uploaded csv file
    row_num = models.IntegerField(_('Row #'))
    # action_taken can be 'insert', 'update' or 'mixed'
    action_taken = models.CharField(_('Action Taken'), max_length=20, null=True)
    error = models.CharField(_('Error'), max_length=500, default='')

    class Meta:
        app_label = 'memberships'


NOTICE_TYPES = (
    ('join', _('Join Date')),
    ('renewal', _('Renewal Date')),
    ('expiration', _('Expiration Date')),
    ('approve', _('Approval Date')),
    ('disapprove', _('Disapproval Date')),
)


class Notice(models.Model):

    NOTICE_BEFORE = 'before'
    NOTICE_AFTER = 'after'
    NOTICE_ATTIMEOF = 'attimeof'

    NOTICE_CHOICES = (
        (NOTICE_BEFORE, _('Before')),
        (NOTICE_AFTER,  _('After')),
        (NOTICE_ATTIMEOF, _('At Time Of'))
    )

    CONTENT_TYPE_HTML = 'html'

    CONTENT_TYPE_CHOICES = (
        (CONTENT_TYPE_HTML, _('HTML')),
    )

    STATUS_DETAIL_ACTIVE = 'active'
    STATUS_DETAIL_HOLD = 'admin_hold'

    STATUS_DETAIL_CHOICES = (
        (STATUS_DETAIL_ACTIVE, 'Active'),
        (STATUS_DETAIL_HOLD, 'Admin Hold')
    )

    guid = models.CharField(max_length=50, editable=False)
    notice_name = models.CharField(_("Name"), max_length=250)
    num_days = models.IntegerField(default=0)
    notice_time = models.CharField(_("Notice Time"), max_length=20, choices=NOTICE_CHOICES)
    notice_type = models.CharField(_("For Notice Type"), max_length=20, choices=NOTICE_TYPES)
    system_generated = models.BooleanField(_("System Generated"), default=False)
    membership_type = models.ForeignKey(
        "MembershipType",
        blank=True,
        null=True,
        help_text=_("Note that if you \
            don't select a membership type, \
            the notice will go out to all members."
    ))

    subject = models.CharField(max_length=255)
    content_type = models.CharField(_("Content Type"),
                                    choices=CONTENT_TYPE_CHOICES,
                                    max_length=10,
                                    default=CONTENT_TYPE_HTML)
    sender = models.EmailField(max_length=255, blank=True, null=True)
    sender_display = models.CharField(max_length=255, blank=True, null=True)
    email_content = tinymce_models.HTMLField(_("Email Content"))

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="membership_notice_creator",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="membership_notice_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(choices=STATUS_DETAIL_CHOICES,
                                     default=STATUS_DETAIL_ACTIVE, max_length=50)
    status = models.BooleanField(default=True)

    class Meta:
        app_label = 'memberships'

    def __unicode__(self):
        return self.notice_name

    @property
    def footer(self):
        return """
        This e-mail was generated by Tendenci&reg; Software - a
        web based membership management software solution
        www.tendenci.com developed by Schipul - The Web Marketing Company
        """

    def get_default_context(self, membership=None):
        """
        Returns a dictionary with default context items.
        """
        global_setting = partial(get_setting, 'site', 'global')
        corporate_msg = u''

        context = {}

        context.update({
            'site_contact_name': global_setting('sitecontactname'),
            'site_contact_email': global_setting('sitecontactemail'),
            'site_display_name': global_setting('sitedisplayname'),
            'time_submitted': time.strftime("%d-%b-%y %I:%M %p", datetime.now().timetuple()),
        })

        # return basic context
        if not membership:
            return context

        # get membership field context
        context.update(membership.get_field_items())

        if membership.corporate_membership_id:
            corporate_msg = """
            <br /><br />
            <font color="#FF0000">
            Organizational Members, please contact your company Membership coordinator
            to ensure that your membership is being renewed.
            </font>
            """

        if membership.expire_dt:
            context.update({
                'expire_dt': time.strftime(
                "%d-%b-%y %I:%M %p",
                membership.expire_dt.timetuple()),
            })
        if membership.payment_method:
            payment_method_name = membership.payment_method.human_name
        else:
            payment_method_name = ''
        context.update({
            'first_name': membership.user.first_name,
            'last_name': membership.user.last_name,
            'email': membership.user.email,
            'username': membership.user.username,
            'member_number': membership.member_number,
            'membership_type': membership.membership_type.name,
            'payment_method': payment_method_name,
            'referer_url': '%s%s?next=%s' % (global_setting('siteurl'), reverse('auth_login'), membership.referer_url),
            'membership_link': '%s%s' % (global_setting('siteurl'), membership.get_absolute_url()),
            'renew_link': '%s%s' % (global_setting('siteurl'), membership.get_absolute_url()),
            'corporate_membership_notice': corporate_msg,
        })

        return context

    def get_subject(self, membership=None):
        """
        Return self.subject replace shortcode (context) variables
        The membership object takes priority over entry object
        """
        context = self.get_default_context(membership)
        return self.build_notice(self.subject, context=context)

    def get_content(self, membership=None):
        """
        Return self.email_content with self.footer appended
        and replace shortcode (context) variables
        """
        content = "%s\n<br /><br />\n%s" % (self.email_content, self.footer)
        context = self.get_default_context(membership)

        return self.build_notice(content, context=context)

    def build_notice(self, content, *args, **kwargs):
        """
        Replace values in a string and return the updated content
        Values are pulled from membership, user, profile, and site_settings
        In the future, maybe we can pull from the membership application entry
        """
        content = fieldify(content)
        template = Template(content)

        context = kwargs.get('context') or {}
        context = Context(context)

        return template.render(context)

    @classmethod
    def log_notices(cls, memberships, **kwargs):
        """
        Log notices for the list of memberships.
        """
        if not memberships:
            return False

        notice_type = kwargs.get('notice_type') or 'joined'
        notice_time = kwargs.get('notice_time') or 'attimeof'
        field_dict = {
            'notice_time': notice_time,
            'notice_type': notice_type,
            'status': True,
            'status_detail': 'active',
        }
        for notice in Notice.objects.filter(**field_dict):
            notice_log = NoticeLog(notice=notice,
                                       num_sent=len(memberships))
            notice_log.save()
            for membership in memberships:
                # log record
                notice_log_record = NoticeDefaultLogRecord(
                                        notice_log=notice_log,
                                        membership=membership)
                notice_log_record.save()
        return True


    @classmethod
    def send_notice(cls, **kwargs):
        """
        Send notice to notice_type specified
        within membership_type specified
        to email addresses specified
        Returns boolean.

        Allowed Notice Types: joined, renewed, approved, disapproved
        """

        notice_type = kwargs.get('notice_type') or 'joined'
        membership_type = kwargs.get('membership_type')
        membership = kwargs.get('membership')
        emails = kwargs.get('emails') or []
        request = kwargs.get('request')

        if not isinstance(membership, MembershipDefault):
            return False

        if isinstance(emails, basestring):
            emails = [emails]  # expecting list of emails

        # allowed notice types
        if notice_type == 'join':
            template_type = 'joined'
        elif notice_type == 'renewal':
            template_type = 'renewed'
        elif notice_type == 'approve':
            template_type = 'approved'
        elif notice_type == 'disapprove':
            template_type = 'disapproved'
        else:
            return False

        # email list required
        if not emails:
            return False

        field_dict = {
            'notice_time': 'attimeof',
            'notice_type': notice_type,
            'status': True,
            'status_detail': 'active',
        }

        # send to applicant
        for notice in Notice.objects.filter(**field_dict):
            notice_requirments = (
                notice.membership_type == membership_type,
                not notice.membership_type
            )

            if any(notice_requirments):
                notification.send_emails(
                    emails,
                    'membership_%s_to_member' % template_type, {
                    'subject': notice.get_subject(membership=membership),
                    'content': notice.get_content(membership=membership),
                    'membership_total': MembershipDefault.objects.filter(status=True, status_detail='active').count(),
                    'reply_to': notice.sender,
                    'sender': get_setting('site', 'global', 'siteemailnoreplyaddress'),
                    'sender_display': notice.sender_display,
                })

        # send email to admins
        membership_recipients = get_notice_recipients('module', 'memberships', 'membershiprecipients')
        admin_recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
        recipients = list(set(membership_recipients + admin_recipients))

        if recipients:
            notification.send_emails(
                recipients,
                'membership_%s_to_admin' % template_type, {
                'request': request,
                'membership': membership,
                'membership_total': MembershipDefault.objects.filter(status=True, status_detail='active').count(),
            })

        return True

    @models.permalink
    def get_absolute_url(self):
        return ('membership.notice_email_content', [self.pk])

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())
        super(Notice, self).save(*args, **kwargs)


class NoticeLog(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice = models.ForeignKey(Notice, related_name="logs")
    notice_sent_dt = models.DateTimeField(auto_now_add=True)
    num_sent = models.IntegerField()

    class Meta:
        app_label = 'memberships'


class NoticeDefaultLogRecord(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice_log = models.ForeignKey(NoticeLog,
                                   related_name="default_log_records")
    membership = models.ForeignKey(MembershipDefault,
                                   related_name="default_log_records")
    action_taken = models.BooleanField(default=False)
    action_taken_dt = models.DateTimeField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'memberships'


class MembershipApp(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)

    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True,
        help_text=_("Description of this application. " + \
        "Displays at top of application."))
    confirmation_text = tinymce_models.HTMLField()
    notes = models.TextField(blank=True, default='')
    use_captcha = models.BooleanField(_("Use Captcha"), default=True)
    allow_multiple_membership = models.BooleanField(_("Allow Multiple Membership Types"),
                            default=False)
    membership_types = models.ManyToManyField(MembershipType,
                                              verbose_name="Membership Types")
    include_tax = models.BooleanField(default=False)
    tax_rate = models.DecimalField(blank=True, max_digits=5, decimal_places=4, default=0,
                                   help_text=_('Example: 0.0825 for 8.25%.'))
    payment_methods = models.ManyToManyField(PaymentMethod,
                                             verbose_name=_("Payment Methods"))
    discount_eligible = models.BooleanField(default=False)
    use_for_corp = models.BooleanField(_("Use for Corporate Individuals"),
                                       default=False)
    objects = MembershipAppManager()

    class Meta:
        verbose_name = _("Membership Application")
        permissions = (("view_app", _("Can view membership application")),)
        app_label = 'memberships'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('membership_default.add', [self.slug])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(MembershipApp, self).save(*args, **kwargs)

    def clone(self):
        """
        Clone this app.
        """
        params = dict([(field.name, getattr(self, field.name)) \
                       for field in self._meta.fields if not field.__class__==AutoField])
        params['slug'] = 'clone-%d-%s' % (self.id, params['slug'])
        params['name'] = 'Clone of %s' % params['name']
        params['slug'] = params['slug'][:200]
        params['name'] = params['name'][:155]
        app_cloned = self.__class__.objects.create(**params)
        # clone fiellds
        fields = self.fields.all()
        for field in fields:
            field.clone(app_cloned)

        return app_cloned

    def application_form_link(self):
        return '<a href="%s">%s</a>' % (
            self.get_absolute_url(), self.slug
        )
    application_form_link.allow_tags = True


class MembershipAppField(OrderingBaseModel):
    LABEL_MAX_LENGTH = 2000
    FIELD_TYPE_CHOICES1 = (
                    ("CharField", _("Text")),
                    ("CharField/django.forms.Textarea", _("Paragraph Text")),
                    ("BooleanField", _("Checkbox")),
                    ("ChoiceField", _("Select One (Drop Down)")),
                    ("ChoiceField/django.forms.RadioSelect", _("Select One (Radio Buttons)")),
                    ("MultipleChoiceField", _("Multi select (Drop Down)")),
                    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi select (Checkboxes)")),
                    ("CountrySelectField", _("Countries Drop Down")),
                    ("EmailField", _("Email")),
                    ("FileField", _("File upload")),
                    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
                    ("DateTimeField", _("Date/time")),
                )
    FIELD_TYPE_CHOICES2 = (
                    ("section_break", _("Section Break")),
                )
    FIELD_TYPE_CHOICES = FIELD_TYPE_CHOICES1 + FIELD_TYPE_CHOICES2

    membership_app = models.ForeignKey("MembershipApp", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    content_type = models.ForeignKey(ContentType,
                                     null=True)
    field_name = models.CharField(max_length=100, blank=True, default='')
    required = models.BooleanField(_("Required"), default=False, blank=True)
    display = models.BooleanField(_("Show"), default=True, blank=True)
    admin_only = models.BooleanField(_("Admin Only"), default=False)

    field_type = models.CharField(_("Field Type"), choices=FIELD_TYPE_CHOICES,
                                  max_length=64)
    description = models.TextField(_("Description"),
                                   max_length=200,
                                   blank=True,
                                   default='')
    help_text = models.CharField(_("Help Text"),
                                 max_length=300,
                                 blank=True,
                                 default='')
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text=_("Comma separated options where applicable"))
    default_value = models.CharField(_("Default Value"),
                                     max_length=200,
                                     blank=True,
                                     default='')
    css_class = models.CharField(_("CSS Class"),
                                 max_length=200,
                                 blank=True,
                                 default='')

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        ordering = ('position',)
        app_label = 'memberships'

    def __unicode__(self):
        if self.field_name:
            return '%s (field name: %s)' % (self.label, self.field_name)
        return '%s' % self.label

    def clone(self, membership_app):
        """
        Clone this field.
        """
        params = dict([(field.name, getattr(self, field.name)) \
                       for field in self._meta.fields if not field.__class__==AutoField])
        cloned_field = self.__class__.objects.create(**params)

        cloned_field.membership_app = membership_app
        cloned_field.save()
        return cloned_field

    def get_field_class(self, initial=None):
        """
            Generate the form field class for this field.
        """
        if self.field_type and self.id:
            if "/" in self.field_type:
                field_class, field_widget = self.field_type.split("/")
            else:
                field_class, field_widget = self.field_type, None
            if field_class == 'CountrySelectField':
                field_class = CountrySelectField
            else:
                field_class = getattr(forms, field_class)
            field_args = {"label": self.label,
                          "required": self.required,
                          'help_text': self.help_text}
            arg_names = field_class.__init__.im_func.func_code.co_varnames
            if initial:
                field_args['initial'] = initial
            else:
                if self.default_value:
                    field_args['initial'] = self.default_value
            if "max_length" in arg_names:
                field_args["max_length"] = FIELD_MAX_LENGTH
            if "choices" in arg_names:
                if self.field_name not in ['membership_type', 'payment_method']:
                    choices = [s.strip() for s in self.choices.split(",")]
                    field_args["choices"] = zip(choices, choices)
            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)

            return field_class(**field_args)
        return None

    @staticmethod
    def get_default_field_type(field_name):
        """
        Get the default field type for the ``field_name``.
        If the ``field_name`` is the name of one of the fields
        in User, Profile, MembershipDefault and MembershipDemographic
        models, the field type is determined via the field.
        Otherwise, default to 'CharField'.
        """
        available_field_types = [choice[0] for choice in
                                 MembershipAppField.FIELD_TYPE_CHOICES]
        user_fields = dict([(field.name, field) \
                        for field in User._meta.fields \
                        if field.get_internal_type() != 'AutoField'])
        fld = None
        field_type = 'CharField'

        if field_name in user_fields:
            fld = user_fields[field_name]
        if not fld:
            profile_fields = dict([(field.name, field) \
                            for field in Profile._meta.fields])
            if field_name in profile_fields:
                fld = profile_fields[field_name]
        if not fld:
            membership_fields = dict([(field.name, field) \
                            for field in MembershipDefault._meta.fields])
            if field_name in membership_fields:
                fld = membership_fields[field_name]

        if fld:
            field_type = fld.get_internal_type()
            if not field_type in available_field_types:
                if field_type in ['ForeignKey', 'OneToOneField']:
                    field_type = 'ChoiceField'
                elif field_type in ['ManyToManyField']:
                    field_type = 'MultipleChoiceField'
                else:
                    field_type = 'CharField'
        return field_type




class MembershipDemographic(models.Model):
    user = models.OneToOneField(User, related_name="demographics", verbose_name=_('user'))

    ud1 = models.TextField(blank=True, default=u'', null=True)
    ud2 = models.TextField(blank=True, default=u'', null=True)
    ud3 = models.TextField(blank=True, default=u'', null=True)
    ud4 = models.TextField(blank=True, default=u'', null=True)
    ud5 = models.TextField(blank=True, default=u'', null=True)
    ud6 = models.TextField(blank=True, default=u'', null=True)
    ud7 = models.TextField(blank=True, default=u'', null=True)
    ud8 = models.TextField(blank=True, default=u'', null=True)
    ud9 = models.TextField(blank=True, default=u'', null=True)
    ud10 = models.TextField(blank=True, default=u'', null=True)
    ud11 = models.TextField(blank=True, default=u'', null=True)
    ud12 = models.TextField(blank=True, default=u'', null=True)
    ud13 = models.TextField(blank=True, default=u'', null=True)
    ud14 = models.TextField(blank=True, default=u'', null=True)
    ud15 = models.TextField(blank=True, default=u'', null=True)
    ud16 = models.TextField(blank=True, default=u'', null=True)
    ud17 = models.TextField(blank=True, default=u'', null=True)
    ud18 = models.TextField(blank=True, default=u'', null=True)
    ud19 = models.TextField(blank=True, default=u'', null=True)
    ud20 = models.TextField(blank=True, default=u'', null=True)
    ud21 = models.TextField(blank=True, default=u'', null=True)
    ud22 = models.TextField(blank=True, default=u'', null=True)
    ud23 = models.TextField(blank=True, default=u'', null=True)
    ud24 = models.TextField(blank=True, default=u'', null=True)
    ud25 = models.TextField(blank=True, default=u'', null=True)
    ud26 = models.TextField(blank=True, default=u'', null=True)
    ud27 = models.TextField(blank=True, default=u'', null=True)
    ud28 = models.TextField(blank=True, default=u'', null=True)
    ud29 = models.TextField(blank=True, default=u'', null=True)
    ud30 = models.TextField(blank=True, default=u'', null=True)

    class Meta:
        app_label = 'memberships'

class MembershipFile(File):
    """
    This model will be used as handlers of File upload assigned
    to User Defined fields for the under Membership demographics
    """
    pass

    class Meta:
        app_label = 'memberships'
