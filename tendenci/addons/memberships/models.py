import os
import re
import hashlib
import uuid
import time
from copy import deepcopy
from functools import partial
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models.query_utils import Q
from django.db import transaction
from django.db import DatabaseError, IntegrityError
from django.template import Context, Template
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.contenttypes import generic
from django import forms
from django.utils.importlib import import_module
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import RequestContext

from tendenci.core.base.utils import day_validate, is_blank
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.utils import get_notice_recipients, has_perm
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.base.fields import DictField
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.user_groups.models import Group
from tendenci.core.emails.models import Email
from tendenci.addons.memberships.managers import MembershipManager, \
    MembershipDefaultManager, MembershipAppManager, MemberAppEntryManager
from tendenci.core.base.utils import fieldify
from tinymce import models as tinymce_models
from tendenci.core.payments.models import PaymentMethod
from tendenci.apps.user_groups.models import GroupMembership
from tendenci.core.event_logs.models import EventLog
from tendenci.apps.profiles.models import Profile
from tendenci.core.files.models import File
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.notifications import models as notification
from tendenci.addons.directories.models import Directory
from tendenci.addons.industries.models import Industry
from tendenci.addons.regions.models import Region
from tendenci.core.base.utils import UnicodeWriter

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^tinymce.models.HTMLField"])
add_introspection_rules([], ["^tendenci.core.base.fields.SlugField"])

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


class MembershipType(OrderingBaseModel, TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.CharField(_('Description'), max_length=500)
    price = models.DecimalField(
        _('Price'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        default=0,
        help_text="Set 0 for free membership."
    )
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
    renewal_require_approval = models.BooleanField(_('Renewal Requires Approval'), default=1)

    admin_only = models.BooleanField(_('Admin Only'), default=0)  # from allowuseroption

    never_expires = models.BooleanField(_("Never Expires"), default=0,
                                        help_text='If selected, skip the Renewal Options.')
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

    fixed_option2_can_rollover = models.BooleanField(_("Allow Rollover"), default=0)
    fixed_option2_rollover_days = models.IntegerField(default=0,
            help_text=_("Membership signups after this date covers the following calendar year as well."))

    renewal_period_start = models.IntegerField(_('Renewal Period Start'), default=30,
            help_text="How long (in days) before the memberships expires can the member renew their membership.")
    renewal_period_end = models.IntegerField(_('Renewal Period End'), default=30,
            help_text="How long (in days) after the memberships expires can the member renew their membership.")
    expiration_grace_period = models.IntegerField(_('Expiration Grace Period'), default=0,
            help_text="The number of days after the membership expires their membership is still active.")

    class Meta:
        verbose_name = "Membership Type"
        permissions = (("view_membershiptype", "Can view membership type"),)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Save GUID if GUID is not set.
        Save MembershipType instance.
        """
        self.guid = self.guid or uuid.uuid1().get_hex()
        super(MembershipType, self).save(*args, **kwargs)

    def get_expiration_dt(self, renewal=False, join_dt=None, renew_dt=None):
        """
        Calculate the expiration date - for join or renew (renewal=True)

        Examples:

            For join:
            expiration_dt = membership_type.get_expiration_dt(join_dt=membership.join_dt)

            For renew:
            expiration_dt = membership_type.get_expiration_dt(renewal=True,
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
                    if (now - expiration_dt).days <= self.fixed_option2_rollover_days:
                        expiration_dt = expiration_dt + relativedelta(years=1)

                return expiration_dt


class MembershipSet(models.Model):
    invoice = models.ForeignKey(Invoice)

    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")

    def memberships(self):
        return MembershipDefault.objects.filter(membership_set=self).order_by('create_dt')

    def save_invoice(self, memberships):
        invoice = Invoice()
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

        invoice.subtotal = price
        invoice.total = price
        invoice.balance = price

        invoice.due_date = datetime.now()
        invoice.ship_date = datetime.now()

        invoice.save()
        self.invoice = invoice
        self.save()

        self.invoice.object_type = ContentType.objects.get(
            app_label=self._meta.app_label, model=self._meta.module_name)

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
    certifications = models.CharField(max_length=500, blank=True)
    work_experience = models.TextField(blank=True)
    referral_source = models.CharField(max_length=150, blank=True)
    referral_source_other = models.CharField(max_length=150, blank=True)
    referral_source_member_name = models.CharField(max_length=50, blank=True, default=u'')
    referral_source_member_number = models.CharField(max_length=50, blank=True, default=u'')
    affiliation_member_number = models.CharField(max_length=50, blank=True)
    join_dt = models.DateTimeField(blank=True, null=True)
    expire_dt = models.DateTimeField(blank=True, null=True)
    renew_dt = models.DateTimeField(blank=True, null=True)
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
    exported = models.BooleanField()
    chapter = models.CharField(max_length=150, blank=True)
    areas_of_expertise = models.CharField(max_length=1000, blank=True)
    corp_profile_id = models.IntegerField(blank=True, default=0)
    corporate_membership_id = models.IntegerField(
        _('Corporate Membership'), blank=True, null=True)
    home_state = models.CharField(max_length=50, blank=True, default=u'')
    year_left_native_country = models.IntegerField(blank=True, null=True)
    network_sectors = models.CharField(max_length=250, blank=True, default=u'')
    networking = models.CharField(max_length=250, blank=True, default=u'')
    government_worker = models.BooleanField()
    government_agency = models.CharField(max_length=250, blank=True, default=u'')
    license_number = models.CharField(max_length=50, blank=True, default=u'')
    license_state = models.CharField(max_length=50, blank=True, default=u'')
    industry = models.ForeignKey(Industry, blank=True, null=True)
    region = models.ForeignKey(Region, blank=True, null=True)
    company_size = models.CharField(max_length=50, blank=True, default=u'')
    promotion_code = models.CharField(max_length=50, blank=True, default=u'')
    directory = models.ForeignKey(Directory, blank=True, null=True)
    groups = models.ManyToManyField(Group, null=True)

    membership_set = models.ForeignKey(MembershipSet, blank=True, null=True)
    app = models.ForeignKey("MembershipApp", null=True)

    objects = MembershipDefaultManager()

    class Meta:
        verbose_name = u'Membership'
        verbose_name_plural = u'Memberships'

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

    def save(self, *args, **kwargs):
        """
        Set GUID if not already set.
        """
        self.guid = self.guid or uuid.uuid1().get_hex()
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
                    field_list.append((
                        field_label,
                        getattr(demographic, field_name)
                    ))

        if is_blank(dict(field_list).values()):
            return []  # empty list

        return field_list

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
        from tendenci.addons.corporate_memberships.models import CorpProfile
        [corporate_profile] = CorpProfile.objects.filter(
            pk=self.corp_profile_id) or [None]

        return corporate_profile

    def get_corporate_membership(self):
        """
        Returns corporate membership object
        else returns None type object.
        """
        from tendenci.addons.corporate_memberships.models import CorpMembership
        [corporate_membership] = CorpMembership.objects.filter(
            pk=self.corp_profile_id) or [None]

        return corporate_membership

    def send_email(self, request, notice_type):
        """
        Convenience method for sending
            typical membership emails.
        Returns outcome via boolean.
        """
        return Notice.send_notice(
            request=request,
            emails=self.user.email,
            notice_type=notice_type,
            membership=self,
            membership_type=self.membership_type,
        )

    def email_corp_reps(self, request):
        """
        Notify corp reps when individuals joined/renewed under a corporation.
        """
        if self.corporate_membership_id:
            from tendenci.addons.corporate_memberships.models import CorpMembership
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
            self.status_detail != 'archive',
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
        if request_user.is_authenticated():  # else: don't set
            self.application_approved_user = request_user

        # application approved/denied ---------------
        self.application_approved_denied_dt = \
            self.application_approved_denied_dt or NOW
        if request_user.is_authenticated():  # else: don't set
            self.application_approved_denied_user = request_user

        # action_taken ------------------------------
        self.action_taken = True
        self.action_taken_dt = self.action_taken_dt or NOW
        if request_user.is_authenticated():  # else: don't set
            self.action_taken_user = request_user

        self.set_join_dt()
        self.set_renew_dt()
        self.set_expire_dt()
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

    def renew(self, request_user):
        """
        Renew this membership.
            - Assert user is in group.
            - Create new invoice.
            - Archive old memberships [of same type].
            - Show member number on profile.

        Will not renew:
            - Archived memberships
        """

        if self.status_detail == 'archive':
            return False

        NOW = datetime.now()

        dupe = deepcopy(self)

        dupe.pk = None  # disconnect from db record

        dupe.status = True,
        dupe.status_detail = 'active'

        # application approved ---------------
        dupe.application_approved = True
        dupe.application_approved_dt = \
            dupe.application_approved_dt or NOW
        if request_user:  # else: don't set
            dupe.application_approved_user = request_user

        # application approved/denied ---------------
        dupe.application_approved_denied_dt = \
            dupe.application_approved_denied_dt or NOW
        if request_user:  # else: don't set
            dupe.application_approved_denied_user = request_user

        # action_taken ------------------------------
        dupe.action_taken = True
        dupe.action_taken_dt = dupe.action_taken_dt or NOW
        if request_user:  # else: don't set
            dupe.action_taken_user = request_user

        dupe.set_join_dt()
        dupe.set_renew_dt()
        dupe.set_expire_dt()
        dupe.save()

        # add to [membership] group
        dupe.group_refresh()

        # new invoice; bound via ct and object_id
        dupe.save_invoice(status_detail='tendered')

        # archive other membership [of this type]
        dupe.archive_old_memberships()

        # show member number on profile
        dupe.user.profile.refresh_member_number()

        return True

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

        if not self.is_approved():
            return False

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
        from dateutil.relativedelta import relativedelta
        grace_period = self.membership_type.expiration_grace_period

        if not self.expire_dt:
            return None

        return self.expire_dt + relativedelta(days=grace_period)

    def is_expired(self):
        """
        status=True, status_detail='active' and has expired,
        includes the grace period.
        """
        if not self.get_expire_dt():
            # there is no grace period, so the member isn't in it
            in_grace_period = False
        else:
            in_grace_period = self.get_expire_dt() < datetime.now()
        is_good = (
            self.status,
            self.status_detail.lower() == 'expired',
            self.get_expire_dt(),
            in_grace_period)

        return all(is_good)

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
        self.status_detail = 'archived'
        """
        return self.status and self.status_detail.lower() == 'archive'

    def get_status(self):
        """
        Returns status of membership
        'pending', 'active', 'disapproved', 'expired', 'archived'
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

        memberships = self.qs_memberships() & \
            (MembershipDefault.QS_ACTIVE() | MembershipDefault.QS_PENDING())

        for membership in memberships:
            if membership != self:
                membership.status_detail = 'archive'
                membership.save()

    def approval_required(self):
        """
        Returns a boolean value on whether approval is required
        This is dependent on whether membership is a join or renewal.
        """
        if self.renewal:
            return self.membership_type.renewal_require_approval
        return self.membership_type.require_approval

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

            if groups:
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
        from tendenci.addons.memberships.utils import spawn_username

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
        # if can't expire, membership is not in the grace period
        if not self.get_expire_dt():
            return False

        return all([self.expire_dt < datetime.now(),
            self.get_expire_dt() > datetime.now(),
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
        end_dt = self.expire_dt + timedelta(
            days=self.membership_type.renewal_period_end + 1
        ) - timedelta(seconds=1)

        return (start_dt, end_dt)

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

        # can only renew from approved state
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
        start_dt, end_dt = renewal_period

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

        form_link = '%s?username=%s&amp;membership_type=%s' % (
            reverse('membership_default.add', kwargs={'slug': self.app.slug}),
            self.user.username,
            self.membership_type.pk)

        approve_link = '%s?approve=' % reverse('membership.details', args=[self.pk])
        disapprove_link = '%s?disapprove' % reverse('membership.details', args=[self.pk])
        expire_link = '%s?expire' % reverse('membership.details', args=[self.pk])

        if self.user.profile.can_renew():
            renew = {form_link: u'Renew Membership'}
        elif is_superuser:
            renew = {form_link: u'Renew Membership'}
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
            app_label=self._meta.app_label, model=self._meta.module_name)

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
            app_label=self._meta.app_label, model=self._meta.module_name)

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
            use_threshold, threshold_price = \
                        self.get_corp_memb_threshold_price(
                                self.corporate_membership_id)
            if use_threshold:
                return threshold_price

        if self.renewal:
            return self.membership_type.renewal_price or 0
        else:
            return self.membership_type.price + (self.membership_type.admin_fee or 0)

    def get_corp_memb_threshold_price(self, corporate_membership_id):
        """
        get the threshold price for individual memberships.
        return tuple (use_threshold, threshold_price)
        """
        from tendenci.addons.corporate_memberships.models import CorpMembership

        [corporate] = CorpMembership.objects.filter(
            id=corporate_membership_id)[:1] or [None]

        if corporate:
            corporate_type = corporate.corporate_membership_type
            threshold = corporate_type.apply_threshold
            threshold_limit = corporate_type.individual_threshold
            threshold_price = corporate_type.individual_threshold_price

            if threshold and threshold_limit > 0:
                membership_count = MembershipDefault.objects.filter(
                    corporate_membership_id=corporate.pk,
                    status=True,
                    status_detail__in=['active',
                                       'pending']
                ).count()
                if membership_count <= threshold_limit:
                    return True, threshold_price
        return False, None

    def qs_memberships(self, **kwargs):
        """
        Get all memberships of this type for this user.
        Breaks if self.user is not set.
        """
        return MembershipDefault.objects.filter(
            user=self.user, membership_type=self.membership_type
        )

    def create_member_number(self):
        """
        Returns a unique member number that is greater than 1000
        and not already taken by a membership record.
        """
        numbers = MembershipDefault.objects.values_list(
            'member_number', flat=True).exclude(member_number=u'')

        numbers = set(numbers)  # remove duplicates
        numbers = [n for n in numbers if n.isdigit()]  # only keep digits
        numbers = map(int, numbers)  # convert strings to ints
        numbers = sorted(numbers)  # sort integers

        count = 1000
        gap_list = []
        for number in numbers:
            while True:
                count += 1
                if count >= number:
                    break
                gap_list.append(count)

        if gap_list:
            return '%s' % gap_list[0]

        if numbers:
            return '%s' % (max(numbers) + 1)

        return '%s' % (count + 1)

    def set_join_dt(self):
        """
        Looks through old memberships to discover join dt
        """

        # cannot set renew dt if approved dt
        # does not exist (DNE)
        if not self.application_approved_dt:
            return None

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
        if not approved:
            self.renew_dt = None
            return None

        memberships = self.qs_memberships(
            ).exclude(status_detail='disapproved'
            ).exclude(status_detail='pending')

        if self.pk:
            memberships = memberships.exclude(pk=self.pk)

        if memberships:
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
        if not approved:
            self.expire_dt = None
            return None

        if self.corporate_membership_id:
            # corp individuals expire with their corporate membership
            from tendenci.addons.corporate_memberships.models import CorpMembership
            [corp_expiration_dt] = CorpMembership.objects.filter(
                                        id=self.corporate_membership_id
                                        ).values_list('expiration_dt',
                                                      flat=True)[:1] or [None]
            self.expire_dt = corp_expiration_dt
        else:
            if self.renew_dt:
                self.expire_dt = self.membership_type.get_expiration_dt(
                    renewal=self.renewal, renew_dt=self.renew_dt
                )
            elif self.join_dt:
                self.expire_dt = self.membership_type.get_expiration_dt(
                    renewal=self.renewal, join_dt=self.join_dt
                )

    def set_member_number(self):
        """
        Sets membership number via previous
        membership record.
        """
        # if member_number; get out
        if self.member_number:
            return None

        memberships = self.qs_memberships().exclude(
            member_number__exact=u'').order_by('-pk')

        if memberships:
            self.member_number = memberships[0].member_number

        if not self.member_number:
            self.member_number = self.create_member_number()

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
            profile = user.profile
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

        from tendenci.addons.corporate_memberships.models import CorpMembership
        [corp_memb] = CorpMembership.objects.filter(
                    pk=self.corporate_membership_id)[:1] or [None]
        return corp_memb

    def membership_type_link(self):
        link = '<a href="%s">%s</a>' % (
                reverse('admin:memberships_membershiptype_change',
                        args=[self.membership_type.id]),
                        self.membership_type.name)
        if self.corporate_membership_id:
            from tendenci.addons.corporate_memberships.models import CorpMembership
            corp_member = CorpMembership.objects.filter(id=self.corporate_membership_id)[:1] or [None]
            if corp_member:
                link = '%s (<a href="%s">corp</a> %s)' % (
                    link,
                    reverse('corpmembership.view',
                            args=[self.corporate_membership_id]),
                    corp_member[0].status_detail)
        return link
    membership_type_link.allow_tags = True
    membership_type_link.short_description = u'Membership Type'

    def auto_update_paid_object(self, request, payment):
        """
        Update membership status and dates. Created archives if
        necessary.  Send out notices.  Log approval event.
        """
        from tendenci.apps.notifications.utils import send_welcome_email

        can_approve = False

        if request.user.profile.is_superuser:
            can_approve = True
        else:
            if (self.renewal and \
                    not self.membership_type.renewal_require_approval) \
                or (not self.renewal and \
                    not self.membership_type.require_approval):
                    can_approve = True

        if can_approve:

            self.user, created = self.get_or_create_user()
            if created:
                send_welcome_email(self.user)

            # auto approve -------------------------
            self.application_approved = True
            self.application_approved_user = self.user
            self.application_approved_dt = datetime.now()
            self.application_approved_denied_user = self.user
            self.status = True
            self.status_detail = 'active'

            self.set_join_dt()
            if self.renewal:
                self.set_renew_dt()
            self.set_expire_dt()
            self.save()

            self.archive_old_memberships()

            # user in [membership] group
            self.group_refresh()

            # show member number on profile
            self.user.profile.refresh_member_number()

            Notice.send_notice(
                request=request,
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


class Membership(TendenciBaseModel):
    """
    Holds all membership records.
    Memberships that are approved, denied, and pending.
    """
    guid = models.CharField(max_length=50)
    member_number = models.CharField(_("Member Number"), max_length=50)
    membership_type = models.ForeignKey("MembershipType", verbose_name=_("Membership Type"))
    user = models.ForeignKey(User, related_name="memberships")
    renewal = models.BooleanField(default=False)
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    subscribe_dt = models.DateTimeField(_("Subscribe Date"))
    expire_dt = models.DateTimeField(_("Expiration Date Time"), null=True)
    corporate_membership_id = models.IntegerField(_('Corporate Membership Id'), default=0)
    payment_method = models.ForeignKey(PaymentMethod, blank=True, null=True)
    ma = models.ForeignKey("App", null=True)
    send_notice = models.BooleanField(default=True)

    perms = generic.GenericRelation(ObjectPermission,
        object_id_field="object_id", content_type_field="content_type")

    objects = MembershipManager()

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
        permissions = (("view_membership", "Can view membership"),)

    def __unicode__(self):
        label = u''
        if hasattr(self, 'user'):
            label = self.user.get_full_name() or self.user.username
        label = "#%s %s" % (self.member_number, label)
        return label.strip()

    @models.permalink
    def get_absolute_url(self):
        return ('membership.details', [self.pk])

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())
        super(Membership, self).save(*args, **kwargs)

    def is_forever(self):
        """
        status=True, status_detail='active' and has
        not expire_dt (within database is NULL).
        """
        return self.is_active() and not self.expire_dt

    def is_active(self):
        """
        status = True, status_detail = 'active', and has not expired
        considers grace period when evaluating expiration date-time
        """
        from dateutil.relativedelta import relativedelta
        grace_period = self.membership_type.expiration_grace_period
        graceful_now = datetime.now() - relativedelta(days=grace_period)

        if self.status and self.status_detail.lower() == 'active':

            # membership does not expire
            if not self.expire_dt:
                return True

            # membership has not expired
            if self.expire_dt > graceful_now:
                return True

        return False

    def get_expire_dt(self):
        from dateutil.relativedelta import relativedelta
        grace_period = self.membership_type.expiration_grace_period
        return self.expire_dt + relativedelta(days=grace_period)

    def get_name(self):

        user = self.user
        profile = user.get_profile()

        name = "%s %s" % (user.first_name, user.last_name)
        name = name.strip()

        return profile.display_name or name or user.email or user.username

    def get_entry(self):
        try:
            entry = self.entries.filter(is_approved=True).order_by('decision_dt')[0]
        except (ObjectDoesNotExist, MultipleObjectsReturned, IndexError):
            entry = None
        return entry

    @property
    def entry_items(self):
        """
        Returns a dictionary of entry items.
        The approved entry that is associated with this membership.
        """
        return self.get_entry_items()

    def get_entry_items(self, slugify_label=True):
        items = {}
        entry = self.get_entry()

        if entry:
            for field in entry.fields.all():
                label = field.field.label
                if slugify_label:
                    label = slugify(label).replace('-', '_')
                items[label] = field.value

        return items

    def get_renewal_period_dt(self):
        """
         Returns a none type object or 2-tuple with start_dt and end_dt
        """
        if not self.membership_type.allow_renewal:
            return None

        if not isinstance(self.expire_dt, datetime):
            return None

        start_dt = self.expire_dt - timedelta(days=self.membership_type.renewal_period_start)
        end_dt = self.expire_dt + timedelta(days=self.membership_type.renewal_period_end)

        return (start_dt, end_dt)

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

        # if never expires; can never renew
        if self.is_forever():
            return False

        # if membership type allows renewals
        if not self.membership_type.allow_renewal:
            return False

        # renewal not allowed; or no renewal period
        if not renewal_period:
            return False

        # can only renew from approved state
        if self.status_detail.lower() != 'active':
            return False

        # assert that we're within the renewal period
        start_dt, end_dt = renewal_period
        return (datetime.now() >= start_dt and datetime.now() <= end_dt)

    @classmethod
    def types_in_contract(cls, user):
        """
        Return a list of membership types that this
        user is still in contract with.

        This means that their a member and they are
        not within their renewal period.
        """

        in_contract = []

        if user.is_anonymous():
            return in_contract

        memberships = cls.objects.filter(user=user)
        for membership in memberships:
            if not membership.can_renew() and membership.status_detail == 'active':
                in_contract.append(membership.membership_type)

        return in_contract

    def allow_view_by(self, this_user):
        if this_user.profile.is_superuser:
            return True

        if this_user.is_anonymous():
            if self.allow_anonymous_view:
                return self.status and self.status_detail == 'active'
        else:
            if this_user in (self.creator, self.owner, self.user):
                return self.status and self.status_detail == 'active'
            elif self.allow_user_view:
                return self.status and self.status_detail == 'active'
            elif has_perm(this_user, 'memberships.view_app', self):
                return True

        return False

    def populate_user_member_id(self, verbosity=1):
        """
        Populate the member ID (or member number) to user profile.
        """
        if self.is_active():
            if self.member_number:
                [profile] = Profile.objects.filter(user=self.user)[:1] or [None]
                if not profile:
                    profile = Profile.objects.create_profile(self.user)

                if any([not profile.member_number,
                       profile.member_number != self.member_number]):
                    profile.member_number = self.member_number
                    profile.save()

                    # set the is_member attr to True for this user
                    setattr(self.user, 'is_member', True)

                    if verbosity > 1:
                        print 'Added member number %s for %s.' % \
                            (self.member_number, self.user.username)
                else:
                    if verbosity > 1:
                        print 'Member number already populated for %s' % self.user.username
            else:
                if verbosity > 1:
                    print '***Membership (ID=%d) does NOT have a member number.' % self.id

    def populate_or_clear_member_id(self):
        """
        If the membership is active, populate the member ID to profile.
        Otherwise, clear the member ID from profile.
        """
        if self.is_active():
            self.populate_user_member_id()
        else:
            self.clear_user_member_id()
            # set the is_member attr to False for this user
            setattr(self.user, 'is_member', False)


class MembershipImport(models.Model):
    INTERACTIVE_CHOICES = (
        (1, 'Interactive'),
        (0, 'Not Interactive (no login)'),
    )

    OVERRIDE_CHOICES = (
        (0, 'Blank Fields'),
        (1, 'All Fields (override)'),
    )

    STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('preprocessing', 'Pre_processing'),
        ('preprocess_done', 'Pre_process Done'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    )

    UPLOAD_DIR = "imports/memberships/%s" % uuid.uuid1().get_hex()[:8]

    app = models.ForeignKey('App', null=True)
    upload_file = models.FileField(_("Upload File"), max_length=260,
                                   upload_to=UPLOAD_DIR,
                                   null=True)
    recap_file = models.FileField(_("Recap File"), max_length=260,
                                   upload_to=UPLOAD_DIR, null=True)
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

    def get_file(self):
        if self.upload_file:
            return self.upload_file

        file = File.objects.get_for_model(self)[0]
        return file

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
            header_row.extend(['action', 'error'])
            recap_writer.writerow(header_row)
            data_list = MembershipImportData.objects.filter(
                mimport=self).order_by('row_num')
            for idata in data_list:
                data_dict = idata.row_data
                row = [data_dict[k] for k in header_row if k not in [
                                            'action', 'error']]
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


NOTICE_TYPES = (
    ('join', 'Join Date'),
    ('renewal', 'Renewal Date'),
    ('expiration', 'Expiration Date'),
    ('approve', 'Approval Date'),
    ('disapprove', 'Disapproval Date'),
)


class Notice(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice_name = models.CharField(_("Name"), max_length=250)
    num_days = models.IntegerField(default=0)
    notice_time = models.CharField(_("Notice Time"), max_length=20,
                                   choices=(('before', 'Before'),
                                            ('after', 'After'),
                                            ('attimeof', 'At Time Of')))
    notice_type = models.CharField(_("For Notice Type"), max_length=20, choices=NOTICE_TYPES)
    system_generated = models.BooleanField(_("System Generated"), default=0)
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
                                    choices=(('html', 'HTML'),
                                            ('text', 'Plain Text')),
                                    max_length=10)
    sender = models.EmailField(max_length=255, blank=True, null=True)
    sender_display = models.CharField(max_length=255, blank=True, null=True)
    email_content = tinymce_models.HTMLField(_("Email Content"))

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="membership_notice_creator",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="membership_notice_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(choices=(('active', 'Active'), ('admin_hold', 'Admin Hold')),
                                     default='active', max_length=50)
    status = models.BooleanField(default=True)

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
        corporate_msg, expire_dt = u'', u''

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

        context.update({
            'first_name': membership.user.first_name,
            'last_name': membership.user.last_name,
            'email': membership.user.email,
            'member_number': membership.member_number,
            'membership_type': membership.membership_type.name,
            'payment_method': membership.payment_method.human_name,
            'membership_link': '%s%s'.format(global_setting('siteurl'), membership.get_absolute_url()),
            'renew_link': '%s%s'.format(global_setting('siteurl'), membership.get_absolute_url()),
            'corporate_membership_notice': corporate_msg,
        })

        return context

    def get_subject(self, membership=None):
        """
        Return self.subject replace shortcode (context) variables
        The membership object takes priority over entry object
        """
        return self.build_notice(self.subject, context={})

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
                notice.membership_type == None
            )

            if any(notice_requirments):
                notification.send_emails(
                    emails,
                    'membership_%s_to_member' % template_type, {
                    'subject': notice.get_subject(membership=membership),
                    'content': notice.get_content(membership=membership),
                    'membership_total': Membership.objects.active().count(),
                    'reply_to': notice.sender,
                    'sender': notice.sender,
                    'sender_display': notice.sender_display,
                })

        # send email to admins
        membership_recipients = get_notice_recipients('module', 'memberships', 'membershiprecipients')
        admin_recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
        recipients = list(set(membership_recipients + admin_recipients))

        if recipients:
            notification.send_emails(recipients,
                'membership_%s_to_admin' % template_type, {
                'request': request,
                'membership': membership,
                'membership_total': Membership.objects.active().count(),
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


class NoticeLogRecord(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice_log = models.ForeignKey(NoticeLog, related_name="log_records")
    membership = models.ForeignKey(Membership, related_name="log_records")
    action_taken = models.BooleanField(default=0)
    action_taken_dt = models.DateTimeField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)


class NoticeDefaultLogRecord(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice_log = models.ForeignKey(NoticeLog,
                                   related_name="default_log_records")
    membership = models.ForeignKey(MembershipDefault,
                                   related_name="default_log_records")
    action_taken = models.BooleanField(default=0)
    action_taken_dt = models.DateTimeField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)


class MembershipApp(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)

    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True,
        help_text="Description of this application. " + \
        "Displays at top of application.")
    confirmation_text = tinymce_models.HTMLField()
    notes = models.TextField(blank=True, default='')
    use_captcha = models.BooleanField(_("Use Captcha"), default=True)
    allow_multiple_membership = models.BooleanField(_("Allow Multiple Membership Types"),
                            default=False)
    membership_types = models.ManyToManyField(MembershipType,
                                              verbose_name="Membership Types")
    payment_methods = models.ManyToManyField(PaymentMethod,
                                             verbose_name="Payment Methods")
    discount_eligible = models.BooleanField(default=False)
    use_for_corp = models.BooleanField(_("Use for Corporate Individuals"),
                                       default=True)
    objects = MembershipAppManager()

    class Meta:
        verbose_name = "Membership Application"
        permissions = (("view_app", "Can view membership application"),)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('membership_default.add', [self.slug])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(MembershipApp, self).save(*args, **kwargs)

    def application_form_link(self):
        return '<a href="%s">%s</a>' % (
            self.get_absolute_url(), self.slug
        )
    application_form_link.allow_tags = True


class MembershipAppField(OrderingBaseModel):
    LABEL_MAX_LENGTH = 2000
    FIELD_TYPE_CHOICES = (
                    ("CharField", _("Text")),
                    ("CharField/django.forms.Textarea", _("Paragraph Text")),
                    ("BooleanField", _("Checkbox")),
                    ("ChoiceField", _("Select One (Drop Down)")),
                    ("ChoiceField/django.forms.RadioSelect", _("Select One (Radio Buttons)")),
                    ("MultipleChoiceField", _("Multi select (Drop Down)")),
                    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi select (Checkboxes)")),
                    ("EmailField", _("Email")),
                    ("FileField", _("File upload")),
                    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
                    ("DateTimeField", _("Date/time")),
                    ("section_break", _("Section Break")),
                )

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
                                 max_length=200,
                                 blank=True,
                                 default='')
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text="Comma separated options where applicable")
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

    def __unicode__(self):
        if self.field_name:
            return '%s (field name: %s)' % (self.label, self.field_name)
        return '%s' % self.label

    def get_field_class(self, initial=None):
        """
            Generate the form field class for this field.
        """
        if self.field_type and self.id:
            if "/" in self.field_type:
                field_class, field_widget = self.field_type.split("/")
            else:
                field_class, field_widget = self.field_type, None
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
                    choices = self.choices.split(",")
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


class App(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)

    name = models.CharField(_("Application Name"), max_length=155)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True,
        help_text="Description of this application. Displays at top of application.")
    confirmation_text = tinymce_models.HTMLField()
    notes = tinymce_models.HTMLField(blank=True)
    use_captcha = models.BooleanField(_("Use Captcha"), default=1)
    membership_types = models.ManyToManyField(MembershipType, verbose_name="Membership Types")
    payment_methods = models.ManyToManyField(PaymentMethod, verbose_name="Payment Methods")

    use_for_corp = models.BooleanField(_("Use for Corporate Individuals"), default=0)

    class Meta:
        verbose_name = "Membership Application"
        permissions = (("view_app", "Can view membership application"),)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('membership.application_details', [self.slug])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(App, self).save(*args, **kwargs)

    def get_prefill_kwargs(self, membership=None):
        """
        Prefill this application.
        Possible Parameters: user, membership, entry
        """
        entry = membership.ma.entries.order_by('-pk')[0]
        init_kwargs = [(f.field.pk, f.value) for f in entry.fields.all()]

        return dict(init_kwargs)

    def get_initial_info(self, user):
        """
        Get initial information to pre-populate application.
        First look for a previously submitted application.
        Else get initial user information from user/profile and populate.
        Return an initial-dictionary.
        """
        from django.contrib.contenttypes.models import ContentType

        initial = {}
        if user.is_anonymous():
            return initial

        # querying for previously submitted forms
        entries = user.appentry_set.filter(app=self).order_by('-pk')
        if entries:
            initial = dict([(f.field.pk, f.value) for f in entries[0].fields.all()])
            return initial

        # getting fn, ln, em from user/profile record
        user_ct = ContentType.objects.get_for_model(user)
        for field in self.fields.filter(content_type=user_ct):
            if field.field_type == 'first-name':
                initial['field_%s' % field.pk] = user.first_name
            elif field.field_type == 'last-name':
                initial['field_%s' % field.pk] = user.last_name
            elif field.field_type == 'email':
                initial['field_%s' % field.pk] = user.email

        return initial

    def allow_view_by(self, this_user):
        if this_user.profile.is_superuser:
            return True

        if this_user.is_anonymous():
            if self.allow_anonymous_view:
                return self.status and self.status_detail in ['active', 'published']
        else:
            if this_user in (self.creator, self.owner):
                return self.status and self.status_detail in ['active', 'published']
            elif self.allow_user_view:
                return self.status and self.status_detail in ['active', 'published']
            elif has_perm(this_user, 'memberships.view_app', self):
                return True

        return False


class AppFieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True).order_by('position')

    def non_admin_visible(self):
        return self.filter(visible=True, admin_only=False).order_by('position')


class AppField(OrderingBaseModel):
    app = models.ForeignKey("App", related_name="fields")
    content_type = models.ForeignKey(ContentType,
        related_name="membership_app_field_set", editable=False, null=True)
    attribute_name = models.CharField(_("Attribute Name"), max_length=300)
    label = models.CharField(_("Label"), max_length=2000)

    description = models.TextField(_("Description"), max_length=200, blank=True)

    help_text = models.CharField(_("Help Text"), max_length=200, blank=True)
    default_value = models.CharField(_("Default Value"), max_length=200, blank=True)
    css_class = models.CharField(_("CSS Class"), max_length=200, blank=True)

    field_name = models.CharField(max_length=100, blank=True, default='')
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES, max_length=100)
    field_function = models.CharField(_("Special Functionality"),
        choices=FIELD_FUNCTIONS, max_length=64, null=True, blank=True)
    function_params = models.CharField(_("Group Name or Names"),
        max_length=100, null=True, blank=True, help_text="Comma separated if more than one")
    vital = models.BooleanField(_("Vital"), default=False, blank=True)
    required = models.BooleanField(_("Required"), default=False, blank=True)
    visible = models.BooleanField(_("Visible"), default=True, blank=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text="Comma separated options where applicable")

    unique = models.BooleanField(_("Unique"), default=False, blank=True)
    admin_only = models.BooleanField(_("Admin Only"), default=False)
    exportable = models.BooleanField(_("Exportable"), default=True)

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

    def execute_function(self, entry):
        user = entry.user
        if self.field_function == "Group":
            for val in self.function_params.split(','):
                group = Group.objects.get(name=val)
                try:
                    group_membership = GroupMembership.objects.get(group=group, member=user)
                except GroupMembership.DoesNotExist:
                    group_membership = GroupMembership(group=group, member=user)
                    group_membership.creator_id = user.id
                    group_membership.creator_username = user.username
                    group_membership.role = 'subscriber'
                    group_membership.owner_id = user.id
                    group_membership.owner_username = user.username
                    group_membership.save()


class AppEntry(TendenciBaseModel):
    """
    An entry submitted via a membership application.
    """
    app = models.ForeignKey("App", related_name="entries")
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    membership = models.ForeignKey("Membership", related_name="entries",
                                   null=True, on_delete=models.SET_NULL)
    entry_time = models.DateTimeField(_("Date/Time"))
    hash = models.CharField(max_length=40, null=True, default='')
    is_renewal = models.BooleanField()
    is_approved = models.NullBooleanField(_('Approved'), null=True)
    decision_dt = models.DateTimeField(null=True)
    judge = models.ForeignKey(User, null=True, related_name='entries', on_delete=models.SET_NULL)
    invoice = models.ForeignKey(Invoice, null=True)
    perms = generic.GenericRelation(
        ObjectPermission,
        object_id_field="object_id",
        content_type_field="content_type"
    )

    objects = MemberAppEntryManager()

    class Meta:
        verbose_name = _("Application Entry")
        verbose_name_plural = _("Application Entries")
        permissions = (("view_appentry", "Can view membership application entry"),)

    def __unicode__(self):
        return '%s - Submission #%s' % (self.app, self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ('membership.application_entries', [self.pk])

    def allow_view_by(self, this_user):
        if this_user.profile.is_superuser:
            return True

        if this_user.is_anonymous():
            if self.allow_anonymous_view:
                return True
        else:
            if this_user in (self.creator, self.owner):
                return True
            elif self.allow_user_view:
                return True
            elif has_perm(this_user, 'memberships.view_appentry', self):
                return True

        return False

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

    def approval_required(self):
        """
        Returns a boolean value on whether approval is required
        This is dependent on whether membership is a join or renewal.
        """
        if self.is_renewal:
            return self.membership_type.renewal_require_approval
        else:
            return self.membership_type.require_approval

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
            return unicode()

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

        # Get membership type via name
        try:
            entry_field = self.fields.get(field__field_type="membership-type")
            return MembershipType.objects.get(name__exact=entry_field.value.strip())
        except:
            pass

        # Find an older "approved" membership entry ------------
        if self.user:
            entries = AppEntry.objects.filter(
                user=self.user,
                membership__isnull=False,
                create_dt__lt=self.create_dt,
            ).order_by('-create_dt')

            if entries:
                return entries[0].membership.membership_type

        # If the application only has one membership type choice ,use that ------
        membership_types = self.app.membership_types.all()

        if membership_types.count() == 1:
            return membership_types[0]

        # else return none; boom.

    @property
    def payment_method(self):
        """Get PaymentMethod object"""

        # TODO: don't like this; would prefer object column in field_entry
        # TODO: Prone to error; We're depending on a string membership type name
        try:
            [entry_field] = self.fields.filter(
                field__field_type="payment-method")[:1] or [None]
            if entry_field:
                v = entry_field.value.strip()
                if v:
                    return PaymentMethod.objects.get(human_name__exact=v)
        except PaymentMethod.MultipleObjectsReturned:
            return PaymentMethod.objects.filter(
                human_name__exact=entry_field.value.strip()
            )[0]
        except AppFieldEntry.DoesNotExist, PaymentMethod.DoesNotExist:
            pass

        # Find an older "approved" membership entry ------------
        if self.user:
            entries = AppEntry.objects.filter(
                user=self.user,
                membership__isnull=False,
                create_dt__lt=self.create_dt,
            ).order_by('-create_dt')

            if entries:
                return entries[0].membership.payment_method

        # If the application only has one membership type choice ,use that ------
        payment_methods = self.app.payment_methods.all()

        if payment_methods:
            return payment_methods[0]

        # else return none; boom.

    def applicant(self):
        """Get User object"""
        if self.membership:
            return self.membership.user

    def get_expire_dt(self):
        """
        Get the expiration date.
        Consider their corporate membership.

        Members under a corporate membership expire
        when their corporate membership expires.
        """
        from tendenci.addons.corporate_memberships.models import CorporateMembership

        expire_dt = None
        if self.corporate_membership_id:
            try:
                expire_dt = CorporateMembership.objects.get(pk=self.corporate_membership_id).expiration_dt
            except CorporateMembership.DoesNotExist:
                pass

        if not expire_dt:  # membership record not found; new membership
            expire_dt = self.membership_type.get_expiration_dt(join_dt=datetime.now())

        return expire_dt

    def get_or_create_user(self):
        """
        Return a user that's newly created or already existed.
        """
        created = False

        # get user -------------
        if self.user:
            user = self.user
        # elif self.suggested_users():
        #     user_pk, user_label = self.suggested_users()[0]
        #     user = User.objects.get(pk=user_pk)
        else:
            created = True
            user = User.objects.create_user(**{
                'username': self.spawn_username(self.first_name[0], self.last_name),
                'email': self.email,
                'password': hashlib.sha1(self.email).hexdigest()[:6]
            })

        return user, created

    def approve(self):
        """
        - Bind membership with user
            1. authenticated user
            2. suggestions per fn, ln, email
            3. create new user
        - Update user with membership data (fn, ln, email)
        - Bind user with group
        - Update membership status_detail='active'
        - Update decision_dt=datetime.now()

        More than 1 [active] membership of the same type cannot exist
        """

        # get user -------------
        user, created = self.get_or_create_user()

        user.first_name = self.first_name
        user.last_name = self.last_name
        user.email = self.email
        user.save()

        # get judge --------------
        if self.judge and self.judge.is_authenticated():
            judge, judge_pk, judge_username = self.judge, self.judge.pk, self.judge.username
        else:
            judge, judge_pk, judge_username = None, int(), unicode()

        # update old membership [of same type] -----------
        user.memberships.filter(
            membership_type=self.membership_type,
            status=True,
            status_detail__in=['pending', 'active', 'expired']
        ).update(status_detail='archive')

        # look for previous member number
        memberships = user.memberships.order_by('-pk')
        if memberships:
            member_number = memberships[0].member_number
        else:
            # all of this to get the largest membership number
            newest_membership = Membership.objects.order_by('-pk')
            if newest_membership:
                member_number = newest_membership[0].pk + 1000
            else:
                member_number = 1000

        membership = Membership.objects.create(**{
            'member_number': member_number,
            'membership_type': self.membership_type,
            'user': user,
            'renewal': self.membership_type.renewal,
            'subscribe_dt': datetime.now(),
            'expire_dt': self.get_expire_dt(),
            'payment_method': self.payment_method,
            'ma': self.app,
            'corporate_membership_id': self.corporate_membership_id,
            'creator': user,
            'creator_username': user.username,
            'owner': user,
            'owner_username': user.username,
        })

        # populate the member number to profile
        membership.populate_user_member_id()

        try:
            # add user to group
            GroupMembership.objects.create(**{
                'group': self.membership_type.group,
                'member': user,
                'creator_id': judge_pk or user.pk,
                'creator_username': judge_username,
                'owner_id': judge_pk or user.pk,
                'owner_username': judge_username,
                'status': True,
                'status_detail': 'active',
            })
        except:
            pass

        # add user to the groups they checked
        field_entries = self.fields.all()
        for field_entry in field_entries:
            value = field_entry.value
            if field_entry.field.field_function == "Group" and value:
                for val in field_entry.field.function_params.split(','):
                    group = Group.objects.get(name=val)
                    try:
                        GroupMembership.objects.create(**{
                            'group': group,
                            'member': user,
                            'creator_id': judge_pk or user.pk,
                            'creator_username': judge_username,
                            'owner_id': judge_pk or user.pk,
                            'owner_username': judge_username,
                            'status': True,
                            'status_detail': 'active',
                        })
                    except:
                        pass

        #Update invoice
        if self.invoice:
            self.invoice.bill_to_first_name = self.user.first_name
            self.invoice.bill_to_last_name = self.user.last_name
            self.invoice.owner = self.user
            self.invoice.owner_username = self.user.username
            self.invoice.save()

        self.is_approved = True
        self.decision_dt = membership.create_dt
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

    def suggested_users(self, **kwargs):
        """
        Return list of users.
        List of users is created via fn, ln, and email passed.
        """
        from operator import __or__ as OR

        kwargs = kwargs or {'email': self.email}

        users = {}
        lst = []
        for i in kwargs.items():
            key, value = i
            if value:
                lst.append(Q(i))

        if lst:
            for u in User.objects.filter(reduce(OR, lst)):
                users[u.pk] = ' '.join([u.first_name, u.last_name, u.username, u.email])

        return users.items()

    def spawn_username(self, *args, **kwargs):
        """
        Join arguments to create username [string].
        Find similiar usernames; auto-increment newest username.
        Return new username [string].
        """
        if not args:
            raise Exception('spawn_username() requires atleast 1 argument; 0 were given')

        max_length = kwargs.get(u'max_length', 9)
        delimiter = kwargs.get(u'delimiter', u'')

        un = ' '.join(args)  # concat args into one string
        un = re.sub('\s+', delimiter, un)  # replace spaces w/ delimiter (default: no-space)
        un = re.sub('[^\w.-]+', u'', un)  # remove non-word-characters
        un = un.strip('_.- ')  # strip funny-characters from sides
        un = un[:max_length].lower()  # keep max length and lowercase username

        others = []  # find similiar usernames
        for u in User.objects.filter(username__startswith=un):
            if u.username.replace(un, '0').isdigit():
                others.append(int(u.username.replace(un, '0')))

        if others and 0 in others:
            # the appended digit will compromise the username length
            # there would have to be more than 99,999 duplicate usernames
            # to kill the database username max field length
            un = '%s%s' % (un, unicode(max(others) + 1))

        return un.lower()

    @property
    def status_msg(self):
        status = 'Pending'

        if self.is_approved:  # property
            status = 'Approved'
        elif self.is_disapproved():  # method
            status = 'Disapproved'

        return status

    def is_pending(self):
        return not self.is_approved

    def is_disapproved(self):
        return not self.is_approved

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

    # to lookup for the number, go to /accountings/account_numbers/
    def get_acct_number(self, discount=False):
        if discount:
            return 462000
        else:
            return 402000

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        If auto-approve; approve entry; send emails; log.
        """
        from tendenci.apps.notifications.utils import send_welcome_email

        if self.is_renewal:
            # if auto-approve renews
            if not self.membership_type.renewal_require_approval:
                self.user, created = self.get_or_create_user()
                if created:
                    send_welcome_email(self.user)
                self.approve()
        else:
            # if auto-approve joins
            if not self.membership_type.require_approval:
                self.user, created = self.get_or_create_user()
                if created:
                    send_welcome_email(self.user)
                self.approve()

        if self.is_approved:

            # silence old memberships within renewal period
            Membership.objects.silence_old_memberships(self.user)

            # send "approved" notification
            Notice.send_notice(
                request=request,
                emails=self.email,
                notice_type='approve',
                membership=self.membership,
                membership_type=self.membership_type,
            )

            # log entry approval
            EventLog.objects.log(**{
                'event_id': 1082101,
                'event_data': '%s (%d) approved by %s' % (self._meta.object_name, self.pk, self.judge),
                'description': '%s viewed' % self._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': self,
            })

    def save_invoice(self, **kwargs):
        status_detail = kwargs.get('status_detail', 'tendered')

        content_type = ContentType.objects.get(
            app_label=self._meta.app_label,
            model=self._meta.module_name
        )

        try:  # get invoice
            invoice = Invoice.objects.get(
                object_type=content_type,
                object_id=self.pk,
            )
        except:  # else; create invoice
            invoice = Invoice()
            invoice.object_type = content_type
            invoice.object_id = self.pk

        # update invoice with details
        invoice.estimate = True
        invoice.status_detail = status_detail

        invoice.bill_to = '%s %s' % (self.first_name, self.last_name)
        invoice.bill_to_first_name = self.first_name
        invoice.bill_to_last_name = self.last_name
        invoice.bill_to_email = self.email

        # if this membership is under a corporate and its corporate membership allows
        # threshold and the threshold is whithin limit, then this membership gets the
        # threshold price.

        (use_threshold, threshold_price) = self.get_corp_memb_threshold_price()
        membership_price = self.get_memb_price()

        if use_threshold:
            invoice.subtotal = threshold_price
            invoice.total = threshold_price
            invoice.balance = threshold_price
        else:
            invoice.subtotal = membership_price
            invoice.total = membership_price
            invoice.balance = membership_price

        invoice.due_date = datetime.now()  # TODO: change model field to null=True
        invoice.ship_date = datetime.now()  # TODO: change model field to null=True

        invoice.save()

        self.invoice = invoice
        self.save()

        return invoice

    def get_memb_price(self):
        membership_price = self.membership_type.price
        if self.membership_type.admin_fee:
            membership_price = self.membership_type.price + self.membership_type.admin_fee
        return membership_price

    def get_corp_memb_threshold_price(self):
        """
        get the threshold price for this individual.
        return tuple (use_threshold, threshold_price)
        """
        from tendenci.addons.corporate_memberships.models import CorporateMembership
        try:
            corp_memb = CorporateMembership.objects.get(id=self.corporate_membership_id)
        except CorporateMembership.DoesNotExist:
            corp_memb = None

        if corp_memb:
            allow_threshold = corp_memb.corporate_membership_type.apply_threshold
            threshold_limit = corp_memb.corporate_membership_type.individual_threshold
            threshold_price = corp_memb.corporate_membership_type.individual_threshold_price
            if self.membership_type.admin_fee:
                threshold_price = corp_memb.corporate_membership_type.individual_threshold_price + self.membership_type.admin_fee

            if allow_threshold and threshold_limit and threshold_limit > 0:
                # check how many memberships have joined under this corporate
                field_entries = AppFieldEntry.objects.filter(
                    field__field_type='corporate_membership_id',
                    value=corp_memb.id
                )
                count = field_entries.count()
                if count <= threshold_limit:
                    return True, threshold_price

        return False, None

    def execute_field_functions(self):
        app = self.app
        fields = app.fields.exclude(field_function=None)
        for field in fields:
            field.execute_function(self)

    @property
    def items(self):
        """
        Returns a dictionary of entry fields.
        """
        return self.get_items()

    def get_items(self, slugify_label=True):
        items = {}
        entry = self

        if entry:
            for field in entry.fields.all():
                label = field.field.label
                if slugify_label:
                    label = slugify(label).replace('-', '_')
                items[label] = field.value

        return items

    def ordered_fields(self):
        return self.fields.all().order_by('field__position')


class AppFieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a membership application.
    """
    entry = models.ForeignKey("AppEntry", related_name="fields")
    field = models.ForeignKey("AppField", related_name="field")
    value = models.CharField(max_length=2000)

    def __unicode__(self):
        return "%s %s" % (self.field.label, self.value)

    class Meta:
        verbose_name = _("Application Field Entry")
        verbose_name_plural = _("Application Field Entries")

    def corporate_membership_name(self):
        if self.field.field_type == 'corporate_membership_id':
            try:
                #from tendenci.addons.corporate_memberships.models import CorporateMembership
                from django.db import connection
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT name
                    FROM corporate_memberships_corporatemembership
                    WHERE id=%d
                    LIMIT 1 """ % int(self.value))
                rows = cursor.fetchall()
                if rows:
                    return rows[0][0]
            except:
                pass

        return None


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


# Moved from management/__init__.py to here because it breaks
# the management commands due to the ImportError.
# assign models permissions to the admin auth group
def assign_permissions(app, created_models, verbosity, **kwargs):
    from tendenci.core.perms.utils import update_admin_group_perms
    update_admin_group_perms()
from django.db.models.signals import post_syncdb
#from memberships import models as membership_models
post_syncdb.connect(assign_permissions, sender=__file__)
