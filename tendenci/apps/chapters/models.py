from datetime import date, datetime, timedelta
import time
import uuid
import os
from dateutil.relativedelta import relativedelta
import traceback
import logging
from csv import reader
import hashlib

from django.db.models import Q
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.template.defaultfilters import slugify
from django import forms
from django.utils.safestring import mark_safe
from django.template import engines
from django.core.files.storage import default_storage
from importlib import import_module

from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.pages.models import BasePage
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.chapters.managers import (ChapterManager,
                    ChapterMembershipTypeManager,
                    ChapterMembershipManager,
                    ChapterMembershipAppManager)
from tendenci.apps.chapters.module_meta import ChapterMeta
from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.apps.entities.models import Entity
from tendenci.apps.files.models import File
from tendenci.apps.base.fields import SlugField, CountrySelectField
from tendenci.apps.regions.models import Region
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.payments.models import PaymentMethod
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.files.validators import FileValidator
from tendenci.apps.base.utils import tcurrency, day_validate
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import fieldify
from tendenci.apps.base.utils import validate_email
from tendenci.apps.notifications import models as notification
from tendenci.apps.base.models import BaseImport, BaseImportData
from tendenci.apps.base.utils import UnicodeWriter
from tendenci.apps.base.utils import correct_filename
from tendenci.apps.event_logs.models import EventLog

logger = logging.getLogger(__name__)


class Chapter(BasePage):
    """
    Chapters module. Similar to Pages with extra fields.
    """
    slug = SlugField(_('URL Path'), unique=True)
    entity = models.OneToOneField(Entity, null=True,
                                  on_delete=models.SET_NULL,)
    mission = tinymce_models.HTMLField(null=True, blank=True)
    notes = tinymce_models.HTMLField(null=True, blank=True)
    sponsors =tinymce_models.HTMLField(blank=True, default='')
    featured_image = models.ForeignKey(File, null=True, default=None,
                              related_name='chapters',
                              help_text=_('Only jpg, gif, or png images.'),
                              on_delete=models.SET_NULL)
    contact_name = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    join_link = models.CharField(max_length=200, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    newsletter_group = models.ForeignKey(Group, null=True, blank=True,
                                         related_name='ng_chapters',
                                         on_delete=models.CASCADE)
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL)
    county = models.CharField(_('county'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True, default='')
    external_payment_link = models.URLField(_('External payment link'),
                blank=True, default='',
                help_text=_('A third party payment link. If specified, users will be redirected to it to pay their chapter memberships dues online.'))

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = ChapterManager()

    def __str__(self):
        return str(self.title)

    class Meta:
        app_label = 'chapters'

    def get_absolute_url(self):
        return reverse('chapters.detail', args=[self.slug])

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return ChapterMeta().get_meta(self, name)

    def officers(self):
        return Officer.objects.filter(chapter=self).order_by('pk')
    
    def save(self, *args, **kwargs):
        if not self.id:
            setattr(self, 'entity', None)
            setattr(self, 'group', None)
            # auto-generate a group and an entity
            self._auto_generate_entity()
            self._auto_generate_group()

        photo_upload = kwargs.pop('photo', None)

        super(Chapter, self).save(*args, **kwargs)
        if photo_upload and self.pk:
            image = File(content_type=ContentType.objects.get_for_model(self.__class__),
                         object_id=self.pk,
                         creator=self.creator,
                         creator_username=self.creator_username,
                         owner=self.owner,
                         owner_username=self.owner_username)
            photo_upload.file.seek(0)
            image.file.save(photo_upload.name, photo_upload)
            image.save()

            self.featured_image = image
            self.save()

    def _auto_generate_group(self):
        if not (hasattr(self, 'group') and self.group):
            # create a group for this type
            group = Group()
            group.name = f'{self.title}'[:200]
            group.slug = slugify(group.name)
            # ensure uniqueness of the slug
            if Group.objects.filter(slug=group.slug).exists():
                tmp_groups = Group.objects.filter(slug__istartswith=group.slug)
                if tmp_groups:
                    t_list = [g.slug[len(group.slug):] for g in tmp_groups]
                    num = 1
                    while str(num) in t_list:
                        num += 1
                    group.slug = f'{group.slug}{str(num)}'
                    # group name is also a unique field
                    group.name = f'{group.name}{str(num)}'

            group.label = self.title
            group.type = 'distribution'
            group.email_recipient = self.creator and self.creator.email or ''
            group.show_as_option = False
            group.allow_self_add = False
            group.allow_self_remove = False
            group.show_for_memberships = False
            group.description = "Auto-generated with the chapter."
            group.notes = "Auto-generated with the chapter. Used for chapters only"
            #group.use_for_membership = 1
            group.creator = self.creator
            group.creator_username = self.creator_username
            group.owner = self.creator
            group.owner_username = self.owner_username
            group.entity = self.entity

            group.save()

            self.group = group

    def _auto_generate_entity(self):
        if not (hasattr(self, 'entity') and self.entity):
            # create an entity
            entity = Entity.objects.create(
                    entity_name=self.title[:200],
                    entity_type='Chapter',
                    email=self.creator and self.creator.email or '',
                    allow_anonymous_view=False)
            self.entity = entity

    def update_group_perms(self, **kwargs):
        """
        Update the associated group perms for the officers of this chapter. 
        Grant officers the view and change permissions for their own group.
        """
        if not self.group:
            return
 
        ObjectPermission.objects.remove_all(self.group)
    
        perms = ['view', 'change']

        officer_users = [officer.user for officer in self.officers(
            ).filter(Q(expire_dt__isnull=True) | Q(expire_dt__gte=date.today()))]
        if officer_users:
            ObjectPermission.objects.assign(officer_users,
                                        self.group, perms=perms)

    def is_chapter_leader(self, user):
        """
        Check if this user is one of the chapter leaders.
        """
        if not user.is_anonymous:
            return self.officers().filter(Q(expire_dt__isnull=True) | Q(
                expire_dt__gte=date.today())).filter(user=user).exists()

        return False

    def is_chapter_member(self, user):
        if not user.is_anonymous:
            return self.chaptermembership_set.filter(user=user).exists()

        return False


class Position(models.Model):
    title = models.CharField(_(u'title'), max_length=200)

    class Meta:
        app_label = 'chapters'

    def __str__(self):
        return str(self.title)


class Officer(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    user = models.ForeignKey(User,  related_name="%(app_label)s_%(class)s_user", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=120, null=True, blank=True)
    expire_dt = models.DateField(_('Expire Date'), blank=True, null=True,
                                 help_text=_('Leave it blank if never expires.'))

    class Meta:
        app_label = 'chapters'

    def __str__(self):
        return "%s" % self.pk


class ChapterMembershipType(OrderingBaseModel, TendenciBaseModel):
    PRICE_FORMAT = '%s - %s'
    ADMIN_FEE_FORMAT = ' (+%s admin fee)'
    RENEW_FORMAT = ' Renewal'
    PERIOD_CHOICES = (
        ("fixed", _("Fixed")),
        ("rolling", _("Rolling")),
    )
    PERIOD_UNIT_CHOICES = (
        ("days", _("Days")),
        ("months", _("Months")),
        ("years", _("Years")),
    )

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

    require_approval = models.BooleanField(_('Require Approval'), default=True)
    require_payment_approval = models.BooleanField(
        _('Auto-approval requires payment'), default=True,
        help_text=_('If checked, auto-approved memberships will require a successful online payment to be auto-approved.'))
    allow_renewal = models.BooleanField(_('Allow Renewal'), default=True, help_text=_("If not selected, then this membership type cannot be renewed."))
    renewal = models.BooleanField(_('Renewal Only'), default=False, help_text=_("Reserve this membership type for renewals only, not available to new members."))
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
            help_text=_("The number of days (maximum 100) after the membership expires their membership is still active."))

    objects = ChapterMembershipTypeManager()

    class Meta:
        verbose_name = _("Chapter Membership Type")
        app_label = 'chapters'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Save GUID if GUID is not set.
        Save MembershipType instance.
        """
        self.guid = self.guid or uuid.uuid4().hex
        super(ChapterMembershipType, self).save(*args, **kwargs)

    def get_price_display(self, renew_mode=False, chapter=None):
        price = self.price
        renewal_price = self.renewal_price
        if chapter:
            customized_type = (self.customized_types.filter(chapter=chapter)[:1] or [None])[0]
            if customized_type:
                price = customized_type.price
                renewal_price = customized_type.renewal_price
                    
        if renew_mode:
            price_display = f'{self.name} - {tcurrency(renewal_price)} Renewal'
        else:
            price_display = f'{self.name} - {tcurrency(price)}'

        return mark_safe(price_display)


    def get_expiration_dt(self, renewal=False, join_dt=None, renew_dt=None, previous_expire_dt=None):
        """
        Calculate the expiration date - for join or renew (renewal=True)

        Examples:

            For join:
            expiration_dt = membership_type.get_expiration_dt(join_dt=chapter_membership.join_dt)

            For renew:
            expiration_dt = membership_type.get_expiration_dt(renewal=True,
                                                              join_dt=chapter_membership.join_dt,
                                                              renew_dt=chapter_membership.renew_dt,
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
                if expiration_dt <= now:
                    expiration_dt = expiration_dt + relativedelta(years=1)
                if self.fixed_option2_can_rollover:
                    if not self.fixed_option2_rollover_days:
                        self.fixed_option2_rollover_days = 0
                    if (expiration_dt - now).days < self.fixed_option2_rollover_days:
                        expiration_dt = expiration_dt + relativedelta(years=1)

                return expiration_dt


class ChapterMembership(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    member_number = models.CharField(max_length=50, blank=True)
    membership_type = models.ForeignKey(ChapterMembershipType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)

    renewal = models.BooleanField(blank=True, default=False)
    renew_from_id = models.IntegerField(blank=True, null=True)
    certifications = models.CharField(max_length=500, blank=True, default='')
    work_experience = models.TextField(blank=True, default='')
    referral = models.CharField(max_length=500, blank=True, default='')
    expertise = models.CharField(max_length=1000, blank=True, default='')
    occupation = models.CharField(max_length=100, blank=True, default='')
    volunteer_availability = models.BooleanField(default=False)
    social_media_links = models.CharField(max_length=500, blank=True, default='')
    school_type = models.CharField(max_length=50, blank=True)
    school_name = models.CharField(max_length=200, blank=True, default='')
    
    ud1 = models.TextField(blank=True, default='')
    ud2 = models.TextField(blank=True, default='')
    ud3 = models.TextField(blank=True, default='')
    ud4 = models.TextField(blank=True, default='')
    ud5 = models.TextField(blank=True, default='')
    ud6 = models.TextField(blank=True, default='')
    ud7 = models.TextField(blank=True, default='')
    ud8 = models.TextField(blank=True, default='')
    ud9 = models.TextField(blank=True, default='')
    ud10 = models.TextField(blank=True, default='')
    ud11 = models.TextField(blank=True, default='')
    ud12 = models.TextField(blank=True, default='')
    ud13 = models.TextField(blank=True, default='')
    ud14 = models.TextField(blank=True, default='')
    ud15 = models.TextField(blank=True, default='')

    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    join_dt = models.DateTimeField(_('Join Date'), blank=True, null=True)
    expire_dt = models.DateTimeField(_('Expire Date'), blank=True, null=True)
    renew_dt = models.DateTimeField(_('Renew Date'), blank=True, null=True)
    approved = models.BooleanField(default=False)
    approve_dt = models.DateTimeField(_('Approved Date'), blank=True, null=True)
    approved_user = models.ForeignKey(
        User, related_name='chaptermembership_approved_set', null=True,
        on_delete=models.SET_NULL)
    rejected = models.BooleanField(default=False)
    rejected_dt = models.DateTimeField(_('Rejected Date'), blank=True, null=True)
    rejected_user = models.ForeignKey(
        User, related_name='chaptermembership_rejected_set', null=True,
        on_delete=models.SET_NULL)

    payment_received_dt = models.DateTimeField(null=True)
    payment_method = models.ForeignKey(PaymentMethod, null=True,
                                       on_delete=models.SET_NULL)
    invoice = models.ForeignKey(Invoice, null=True, on_delete=models.CASCADE)

    app = models.ForeignKey("ChapterMembershipApp", null=True, on_delete=models.SET_NULL)

    objects = ChapterMembershipManager()

    class Meta:
        verbose_name = _('Chapter Membership')
        verbose_name_plural = _('Chapter Memberships')
        app_label = 'chapters'

    def __str__(self):
        return f"Chapter Membership {self.pk} for {self.user.get_full_name()} in chapter {self.chapter}"

    def get_absolute_url(self):
        """
        Returns admin change_form page.
        """
        return reverse('chapters.membership_details', args=[self.pk])

    def allow_edit_by(self, request_user):
        if request_user.is_superuser or \
            self.chapter.is_chapter_leader(request_user) or \
            self.user == request_user:
            return True

        return False

    def allow_adjust_invoice_by(self, request_user):
        """
        Returns whether or not the request_user can adjust invoice
        for this chapter membership.
        """
        if not request_user.is_anonymous:
            return request_user.is_superuser or \
                 self.chapter.is_chapter_leader(request_user)

        return False

    @property
    def use_third_party_payment(self):
        return get_setting('module', 'chapters', 'usethirdpartypayment')

    @property
    def external_payment_link(self):
        if self.use_third_party_payment:
            return self.chapter.external_payment_link
        return ''

    def create_member_number(self):
        #TODO: Decide how member numbers should be generated for chapter members
        return str(self.id)

    def set_member_number(self):
        """
        Sets chapter membership number via previous record, or from their
        regular membership.
        """
        if not self.member_number:
            [member_number] = ChapterMembership.objects.filter(
                    user=self.user, chapter=self.chapter).exclude(
                        member_number='').order_by('-pk'
                        ).values_list('member_number', flat=True)[:1] or [None]

            if not member_number:
                [member_number] = self.user.membershipdefault_set.filter(
                    status=True).exclude(member_number='').order_by('-pk'
                        ).values_list('member_number', flat=True)[:1] or [None]

            if not member_number:
                member_number = self.create_member_number()

            self.member_number = member_number

        return self.member_number

    def get_since_dt(self):
        chapter_memberships = ChapterMembership.objects.filter(
            user=self.user,
            chapter=self.chapter,
            status=True,
            join_dt__isnull=False
        ).order_by('pk')

        return chapter_memberships[0].join_dt if chapter_memberships else self.create_dt

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
        if self.get_status() not in ['active', 'expired']:
            return False

        # assert that we're within the renewal period
        start_dt, end_dt = renewal_period
        return (datetime.now() >= start_dt and datetime.now() <= end_dt)

    def get_actions(self, user):
        """
        Returns a list of tuples with (link, label)
 
        Possible actions:
            approve
            disapprove
            make pending
            archive
        """
        actions = []
        status = self.get_status()
 
        is_superuser = user.is_superuser
        is_chapter_leader = self.chapter.is_chapter_leader(user)
 
        renew_link = ''
 
        details_link = reverse('chapters.membership_details', args=[self.pk])
        approve_link = f'{details_link}?approve'
        disapprove_link = f'{details_link}?disapprove'
        expire_link = f'{details_link}?expire'
 
        if self.can_renew() and renew_link:
            actions.append((renew_link, _('Renew')))
        elif (is_superuser or is_chapter_leader) and renew_link:
            actions.append((renew_link, _('Admin: Renew')))
 
        if is_superuser or is_chapter_leader:
            if status == 'active':
                actions.append((expire_link, _('Expire Chapter Membership')))
            elif status == 'pending':
                actions.append((approve_link, _('Approve')))
                actions.append((disapprove_link, _('Disapprove')))
                actions.append((expire_link, _('Expire Chapter Membership')))
            elif status == 'expired':
                actions.append((approve_link, _('Approve Chapter Membership')))
 
        return actions

    def get_price(self):
        customized_type = (self.membership_type.customized_types.filter(chapter=self.chapter)[:1] or [None])[0]
        if self.renewal:
            if customized_type:
                return customized_type.renewal_price
            return self.membership_type.renewal_price or 0
        else:
            if customized_type:
                return customized_type.price
            return self.membership_type.price or 0

    def save_invoice(self, **kwargs):
        creator = kwargs.get('creator')
        if not isinstance(creator, User):
            creator = self.user

        status_detail = kwargs.get('status_detail', 'estimate')

        if not self.invoice:
            invoice = Invoice()
            invoice.entity = self.entity
            invoice.title = "Chapter Membership Invoice"
            content_type = ContentType.objects.get(
                app_label=self._meta.app_label, model=self._meta.model_name)
            invoice.object_type = content_type
            invoice.object_id = self.pk

            invoice.bill_to_user(self.user)
            invoice.ship_to_user(self.user)
            invoice.set_creator(creator)
            invoice.set_owner(self.user)
    
            # price information ----------
            price = self.get_price()

            invoice.subtotal = price
            invoice.total = price
            invoice.balance = price
    
            invoice.due_date = datetime.now()
            invoice.ship_date = datetime.now()
    
            invoice.save()
            self.invoice = invoice
            self.save()

        if status_detail == 'estimate':
            self.invoice.estimate = True
        elif status_detail == 'tendered':
            self.invoice.tender(self.user)

        self.invoice.status_detail = status_detail
        self.invoice.save()

        return self.invoice

    def approval_required(self):
        """
        Returns a boolean value on whether approval is required
        This is dependent on whether membership is a join or renewal.
        """
        if self.renewal:
            if not self.membership_type.renewal_require_approval:
                if not self.membership_type.require_payment_approval \
                  or (self.invoice and self.invoice.balance <= 0):
                    # auto approve if not require approval or paid or free
                    return False
        else: # join
            if not self.membership_type.require_approval:
                if not self.membership_type.require_payment_approval \
                  or (self.invoice and self.invoice.balance <= 0):
                    return False
        return True

    def set_join_dt(self):
        """
        Looks through old memberships first to discover join dt
        """
        # cannot set join dt if not approved
        if not self.approve_dt:
            return None

        # previous chapter memberships with join_dt
        chapter_memberships = ChapterMembership.objects.filter(
                    user=self.user, chapter=self.chapter,
                     join_dt__isnull=False
                    ).exclude(status_detail='disapproved'
                    ).exclude(status_detail='pending')

        if self.pk:
            chapter_memberships = chapter_memberships.exclude(pk=self.pk)

        if chapter_memberships:
            self.join_dt = chapter_memberships[0].join_dt
        else:
            self.join_dt = self.join_dt or self.approve_dt

    def set_renew_dt(self):
        """
        Dependent on self.application_approved and
        self.approve_dt

        If qualified memberships exists for this
        Membership.user set
        Membership.renew_dt = Membership.approve_dt
        """

        approved = (
            self.approved,
            self.approve_dt,
        )

        # if not approved
        # set renew_dt and get out
        if not all(approved):
            self.renew_dt = None
            return None

        if self.renewal:
            self.renew_dt = self.approve_dt

    def set_expire_dt(self):
        """
        User ChapterMembershipType to set expiration dt
        """

        approved = (
            self.approved,
            self.approve_dt,
        )

        # if not approved
        # set expire_dt and get out
        if not all(approved):
            self.expire_dt = None
            return None

        if self.renew_dt:
            if self.renew_from_id:
                [previous_expire_dt] = ChapterMembership.objects.filter(
                                            id=self.renew_from_id).values_list(
                                            'expire_dt', flat=True)[:1] or [None]
            else:
                previous_expire_dt = None
            self.expire_dt = self.membership_type.get_expiration_dt(
                renewal=self.renewal, renew_dt=self.renew_dt, previous_expire_dt=previous_expire_dt
            )
        elif self.join_dt:
            self.expire_dt = self.membership_type.get_expiration_dt(
                renewal=self.renewal, join_dt=self.join_dt
            )

    def group_refresh(self):
        """
        Look at the memberships status and decide
        whether the user should or should not be in
        the group.
        """

        active = (self.status, self.status_detail.lower() == 'active')

        if all(active):  # should be in group; make sure they're in
            self.chapter.group.add_user(self.user)
        else:  # should not be in group; make sure they're out
            GroupMembership.objects.filter(
                member=self.user,
                group=self.chapter.group
            ).delete()

    def archive_old_memberships(self):
        """
        Archive old memberships that are active, pending, and expired
        and of this chapter.  Making sure not to archive the newest membership.
        """
        chapter_memberships = ChapterMembership.objects.filter(
                            user=self.user,
                            chapter=self.chapter).exclude(id=self.id)
        for chapter_membership in chapter_memberships:
            chapter_membership.status_detail = 'archive'
            chapter_membership.save()

    def approve(self, request_user=AnonymousUser()):
        """
        Approve this membership.
            - Assert user is in group.
            - Create new invoice.
            - Archive old memberships [of same type].

        Will not approve:
            - Active memberships
            - Expired memberships
            - Archived memberships
        """
        if self.is_approved():
            return self

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
        self.approved = True
        self.approve_dt = \
            self.approve_dt or NOW

        if request_user and request_user.is_authenticated:  # else: don't set
            self.approved_user = request_user

        # check creator and owner
        if not (self.creator and self.creator_username):
            self.creator = self.user
            self.creator_username = self.user.username
        if not (self.owner and self.owner_username):
            self.owner = self.user
            self.owner_username = self.user.username

        self.set_join_dt()
        self.set_renew_dt()
        self.set_expire_dt()
        self.set_member_number()
        self.save()

        # user in [membership] group
        self.group_refresh()

        # new invoice; bound via ct and object_id
        self.save_invoice(status_detail='tendered')
        
        # if external payment, mark as paid on approval
        if self.use_third_party_payment:
            if self.invoice.balance > 0:
                notes = 'Paid via third party payment.'
                if not self.invoice.admin_notes:
                    self.invoice.admin_notes = notes
                else:
                    self.invoice.admin_notes += '\n' + notes
                self.invoice.make_payment(request_user, self.invoice.balance)

        # archive other membership [of this type] [in this chapter]
        self.archive_old_memberships()

        # email notification to member
        if self.renewal:
            notice_type = 'approve_renewal'
        else:
            notice_type = 'approve'
        self.send_email(notice_type=notice_type)

        return self

    def pend(self):
        """
        Set the membership to pending.
        This should not be a method available
        to the end-user.  Used within membership process.
        """
        if self.status_detail == 'archive':
            return False

        self.status = True
        self.status_detail = 'pending'

        # application approved ---------------
        self.approved = False
        self.approve_dt = None
        self.approved_user = None

        self.set_join_dt()
        self.set_renew_dt()
        self.set_expire_dt()

        # add to chapter group
        self.group_refresh()

        # new invoice; bound via ct and object_id
        self.save_invoice(status_detail='estimate')

        return True

    def disapprove(self, request_user=None):
        """
        Disapprove this chapter membership.

        Will not disapprove:
            - Archived chapter memberships
            - Expired chapter memberships (instead: you should renew it)
        """
        if self.is_expired() or self.status_detail == 'archive':
            return False

        NOW = datetime.now()

        self.status = True
        self.status_detail = 'disapproved'

        # application rejected ---------------
        self.rejected = True
        self.rejected_dt = self.rejected_dt or NOW
        if request_user:  # else: don't set
            self.rejected_user = request_user

        self.save()

        # user in [membership] group
        self.group_refresh()

        # new invoice; bound via ct and object_id
        self.save_invoice(status_detail='tendered')

        # archive other membership [of this type]
        self.archive_old_memberships()

        # email notification to member
        if self.renewal:
            notice_type = 'reject_renewal'
        else:
            notice_type = 'reject'
        self.send_email(notice_type=notice_type)

        return True

    def expire(self, request_user):
        """
        Expire this chapter membership.
            - Set status_detail to 'expired'
            - Remove from group.

        Will only expire approved memberships.
        """

        if self.is_approved() or (self.is_expired() and self.status_detail == 'active'):
            self.status = True
            self.status_detail = 'expired'

            self.save()

            # remove from group
            self.group_refresh()

            return True

        return False

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
        return self.status and self.status_detail == 'pending'

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
        # not datetime.datetime(2021, 11, 9, 0, 0),
        # but datetime.datetime(2021, 11, 9, 23, 59, 59)
        end_dt = self.get_renewal_period_end_dt()

        return (start_dt, end_dt)

    def get_renewal_period_end_dt(self):
        return self.expire_dt + timedelta(
            days=self.membership_type.renewal_period_end + 1
        ) - timedelta(seconds=1)

    def send_email(self, notice_type):
        """
        Convenience method for sending
            typical membership emails.
        Returns outcome via boolean.
        """
        notice_sent =  Notice.send_notices(
                notice_type=notice_type,
                chapter_membership=self,
                membership_type=self.membership_type,
            )

        return notice_sent

    def auto_update_paid_object(self, request, payment):
        """
        Update chapter membership status and dates. Created archives if
        necessary.  Send out notices.  Log approval event.
        """
        open_renewal = (
            self.renewal,
            not self.membership_type.renewal_require_approval)

        open_join = (
            not self.renewal,
            not self.membership_type.require_approval)

        can_approve = all(open_renewal) or all(open_join)
        can_approve = can_approve or request.user.profile.is_superuser

        if can_approve:
            self.approve(request.user)
            EventLog.objects.log(
                instance=self,
                action='chapter_membership_approved'
            )


class ChapterMembershipApp(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)

    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True,
        help_text=_("Description of this application. " +
        "Displays at top of application."))
    confirmation_text = tinymce_models.HTMLField()
    renewal_description = tinymce_models.HTMLField(blank=True, default='')
    renewal_confirmation_text = tinymce_models.HTMLField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    use_captcha = models.BooleanField(_("Use Captcha"), default=True)
    membership_types = models.ManyToManyField(ChapterMembershipType,
                                        verbose_name="Chapter Membership Types")
    payment_methods = models.ManyToManyField(PaymentMethod,
                                             verbose_name=_("Payment Methods"))
    objects = ChapterMembershipAppManager()

    class Meta:
        verbose_name = _("Chapter Membership Application")
        app_label = 'chapters'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('chapters.membership_add_pre')

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())
        super(ChapterMembershipApp, self).save(*args, **kwargs)

    def render_items(self, context):
        for field_name in ['name', 'description', 'confirmation_text']:
            template = engines['django'].from_string(getattr(self, field_name))
            setattr(self, field_name, template.render(context=context))

    def get_app_fields(self, chapter, request_user, field_names_to_exclude=[]):
        """
        Retrieves a list of fields for the chapter.
        """
        app_fields = self.fields.filter(display=True)
        if not (request_user.is_superuser or chapter.is_chapter_leader(request_user)):
            app_fields = app_fields.filter(admin_only=False)
        if field_names_to_exclude:
            app_fields = app_fields.exclude(field_name__in=field_names_to_exclude)
        app_fields = app_fields.order_by('position')
        for field in app_fields:
            [cfield] = field.customized_fields.filter(chapter=chapter)[:1] or [None]
            if cfield:
                field.help_text = cfield.help_text
                field.choices = cfield.choices
                field.default_value = cfield.default_value
        return app_fields


class ChapterMembershipAppField(OrderingBaseModel):
    LABEL_MAX_LENGTH = 2000
    FIELD_TYPE_CHOICES1 = (
                    ("", _("Set to Default")),
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
                    ("DateField/django.forms.widgets.SelectDateWidget", _("Date")),
                    ("DateTimeField", _("Date/time")),
                )
    FIELD_TYPE_CHOICES2 = (
                    ("section_break", _("Section Break")),
                )
    FIELD_TYPE_CHOICES = FIELD_TYPE_CHOICES1 + FIELD_TYPE_CHOICES2

    membership_app = models.ForeignKey("ChapterMembershipApp", related_name="fields", on_delete=models.CASCADE)
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100, blank=True, default='')
    required = models.BooleanField(_("Required"), default=False, blank=True)
    display = models.BooleanField(_("Show"), default=True, blank=True)
    customizable = models.BooleanField(default=False, blank=True,
                        help_text=_('Chapter leaders can customize this field.'))
    admin_only = models.BooleanField(_("Admin Only"), default=False)

    field_type = models.CharField(_("Field Type"), blank=True, choices=FIELD_TYPE_CHOICES,
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
        app_label = 'chapters'

    def __str__(self):
        return str(self.id)
#         if self.field_name:
#             return f'{self.label} (field name: {self.field_name})'
#         return self.label

    def get_field_class(self, initial=None):
        """
            Generate the form field class for this field.
        """
        FIELD_MAX_LENGTH = 2000 
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
            arg_names = field_class.__init__.__code__.co_varnames
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
                    if self.field_name == 'sex':
                        field_args["choices"] = [(s.split(':')[0].strip(), s.split(':')[-1].strip()) for s in choices]
                    else:
                        field_args["choices"] = list(zip(choices, choices))
            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)
            if self.field_type == 'FileField':
                field_args["validators"] = [FileValidator()]

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
                                 ChapterMembershipAppField.FIELD_TYPE_CHOICES]
        fld = None
        field_type = 'CharField'

        chapter_membership_fields = dict([(field.name, field)
                        for field in ChapterMembership._meta.fields])
        if field_name in chapter_membership_fields:
            fld = chapter_membership_fields[field_name]

        if fld:
            field_type = fld.get_internal_type()
            if field_type not in available_field_types:
                if field_type in ['ForeignKey', 'OneToOneField']:
                    field_type = 'ChoiceField'
                elif field_type in ['ManyToManyField']:
                    field_type = 'MultipleChoiceField'
                else:
                    field_type = 'CharField'
        return field_type


class CustomizedAppField(models.Model):
    app_field = models.ForeignKey(ChapterMembershipAppField, related_name="customized_fields", on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('app_field', 'chapter',)
        app_label = 'chapters'


class CustomizedType(models.Model):
    """
    Chapter customized membership type so that chapter can set
    their own price and renewal_price.
    """
    membership_type = models.ForeignKey(ChapterMembershipType,
                                        related_name="customized_types",
                                        on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
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


    class Meta:
        unique_together = ('membership_type', 'chapter',)
        app_label = 'chapters'


def file_directory(instance, filename):
    filename = correct_filename(filename)
    m = hashlib.md5()
    m.update(filename.encode())

    hex_digest = m.hexdigest()[:8]

    return f'chapters/files/{hex_digest}/{filename}'


class ChapterMembershipFile(models.Model):
    """
    This model will be used as handlers of File upload assigned
    to User Defined fields for Chapter Membership UD fields
    """
    chapter_membership = models.ForeignKey("ChapterMembership", related_name="files", on_delete=models.CASCADE)
    field = models.ForeignKey("ChapterMembershipAppField", related_name="files", on_delete=models.CASCADE)
    file = models.FileField(max_length=260, upload_to=file_directory)

    class Meta:
        unique_together = ('chapter_membership', 'field')
        app_label = 'chapters'

    def basename(self):
        return os.path.basename(str(self.file.name))

    def ext(self):
        return os.path.splitext(self.basename())[-1]


NOTICE_TYPES = (
    ('apply', _('Apply Date')),
    ('renewal', _('Renewal Date')),
    ('expiration', _('Expiration Date')),
    ('approve', _('Approval Date')),
    ('reject', _('Reject Date')),
    ('approve_renewal', _('Renewal Approval Date')),
    ('reject_renewal', _('Renewal Reject Date')),
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
    chapter = models.ForeignKey(
        "Chapter",
        blank=True,
        null=True,
        help_text=_("Note that if you don't select a chapter, the notice will go out to all chapter members."),
        on_delete=models.CASCADE)
    membership_type = models.ForeignKey(
        "ChapterMembershipType",
        blank=True,
        null=True,
        help_text=_("Note that if you don't select a membership type, the notice will go out to all members."),
        on_delete=models.CASCADE)
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
    creator = models.ForeignKey(User, related_name="chapter_membership_creator_notices",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=150, null=True)
    owner = models.ForeignKey(User, related_name="chapter_membership_owner_notices", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=150, null=True)
    status_detail = models.CharField(choices=STATUS_DETAIL_CHOICES,
                                     default=STATUS_DETAIL_ACTIVE, max_length=50)
    status = models.BooleanField(default=True)

    class Meta:
        app_label = 'chapters'

    def __str__(self):
        return self.notice_name

    def save(self, *args, **kwargs):
        self.guid = self.guid or str(uuid.uuid4())
        super(Notice, self).save(*args, **kwargs)

    def get_default_context(self, chapter_membership):
        """
        Returns a dictionary with default context items.
        """
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        site_contact_name = get_setting('site', 'global', 'sitecontactname')
        site_contact_email = get_setting('site', 'global', 'sitecontactemail')
        site_url = get_setting('site', 'global', 'siteurl')
        now = datetime.now()
        nowstr = time.strftime("%d-%b-%y %I:%M %p", now.timetuple())
        global_context = {'site_display_name': site_display_name,
                          'site_contact_name': site_contact_name,
                          'site_contact_email': site_contact_email,
                          'time_submitted': nowstr,
                          'sitedisplayname': site_display_name,
                          'sitecontactname': site_contact_name,
                          'sitecontactemail': site_contact_email,
                          'timesubmitted': nowstr,
                          }
        context = {}
        context['chapter_membership'] = chapter_membership
        context.update(global_context)

        if chapter_membership and chapter_membership.expire_dt:
            context.update({
                'expire_dt': time.strftime(
                "%d-%b-%y %I:%M %p",
                chapter_membership.expire_dt.timetuple()),
            })

        if chapter_membership and chapter_membership.payment_method:
            payment_method_name = chapter_membership.payment_method.human_name
        else:
            payment_method_name = ''

        view_link = f'{site_url}{chapter_membership.get_absolute_url()}'
        edit_link = '{0}{1}'.format(site_url, reverse('chapters.membership_edit',
                                    args=[chapter_membership.id]))
        renew_link = '{0}{1}'.format(site_url, reverse('chapters.membership_renew',
                                    args=[chapter_membership.id]))
        if chapter_membership.invoice:
            invoice_link = '{0}{1}'.format(site_url, reverse('invoice.view',
                                        args=[chapter_membership.invoice.id]))
            total_amount = chapter_membership.invoice.total
        else:
            invoice_link = ""
            total_amount = ""
        if chapter_membership.expire_dt:
            expire_dt = time.strftime("%d-%b-%y %I:%M %p",
                                      chapter_membership.expire_dt.timetuple())
        else:
            expire_dt = ''

        context.update({
            'chapter_name': chapter_membership.chapter.title,
            'first_name': chapter_membership.user.first_name,
            'last_name': chapter_membership.user.last_name,
            'email': chapter_membership.user.email,
            'username': chapter_membership.user.username,
            'member_number': chapter_membership.member_number,
            'membership_type': chapter_membership.membership_type.name,
            'membership_price': chapter_membership.get_price(),
            'total_amount': total_amount,
            'payment_method': payment_method_name,
            'expire_dt': expire_dt,
            'view_link': view_link,
            'edit_link': edit_link,
            'renew_link': renew_link,
            'invoice_link': invoice_link
        })

        return context

    def get_subject(self, chapter_membership, context=None):
        """
        Return self.subject replace shortcode (context) variables
        """
        if not context:
            context = self.get_default_context(chapter_membership)
        return self.build_notice(self.subject, context=context)

    def get_content(self, chapter_membership, context=None):
        """
        Return self.email_content with footer appended and replace shortcode
        (context) variables
        """
        content = self.email_content
        if not context:
            context = self.get_default_context(chapter_membership)

        return self.build_notice(content, context=context)

    def build_notice(self, content, *args, **kwargs):
        """
        Replace values in a string and return the updated content
        Values are pulled from chapter_membership, user, profile, and site_settings
        """
        content = fieldify(content)
        template = engines['django'].from_string(content)

        context = kwargs.get('context') or {}

        return template.render(context=context)


    def email_chapter_member(self, chapter_membership, verbosity=1):
        """
        Send emails (with the content of this notice) to this chapter member.
        """

        email_context = {
            'sender_display': self.sender_display,
            'reply_to': self.sender
            }
        email_context.update({'content_type': self.content_type})

        user = chapter_membership.user

        context = self.get_default_context(chapter_membership)

        email_recipient = user.email
        # skip if not a valid email address
        if not validate_email(email_recipient):
            return False

        context.update({'first_name': user.first_name})
        subject = self.get_subject(chapter_membership, context=context)
        subject = subject.replace('(name)',
                                    user.get_full_name())
        body = self.get_content(chapter_membership, context=context)

        email_context.update({
            'subject':subject,
            'content':body})
        if self.sender:
            email_context.update({
                #'sender':notice.sender,
                'reply_to':self.sender})
        if self.sender_display:
            email_context.update({'sender_display':self.sender_display})

        notification.send_emails([email_recipient], 'chapter_membership_notice_email',
                                 email_context)
        if verbosity > 1:
            print('To ', email_recipient, subject)

        return True

    def process_notice(self, chapter_membership=None, verbosity=1):
        """
        Gather a list of chapter memberships that meet the criteria of this notice
        and send email notifications to the members.
        """
        self.chapter_memberships_processed = []
        num_sent = 0
        now = datetime.now()
        if self.notice_time in ['before', 'after']:
            if self.notice_time == 'before':
                start_dt = now + timedelta(days=self.num_days)
            else:
                start_dt = now - timedelta(days=self.num_days)

            chapter_memberships = ChapterMembership.objects.exclude(status_detail__in=('archive',))

            if self.notice_type == 'reject' or self.notice_type == 'reject_renewal':
                chapter_memberships = chapter_memberships.filter(
                                    rejected=True,
                                    rejected_dt__year=start_dt.year,
                                    rejected_dt__month=start_dt.month,
                                    rejected_dt__day=start_dt.day,
                                    )
                if self.notice_type == 'reject':
                    chapter_memberships = chapter_memberships.filter(renewal=False)
                else:
                    chapter_memberships = chapter_memberships.filter(renewal=True)
            elif self.notice_type == 'apply':
                chapter_memberships = chapter_memberships.filter(
                                    create_dt__year=start_dt.year,
                                    create_dt__month=start_dt.month,
                                    create_dt__day=start_dt.day,
                                    renewal=False)
            elif self.notice_type == 'renewal':
                chapter_memberships = chapter_memberships.filter(
                                    renew_dt__year=start_dt.year,
                                    renew_dt__month=start_dt.month,
                                    renew_dt__day=start_dt.day,
                                    renewal=True)
            elif self.notice_type == 'approve' or self.notice_type == 'approve_renewal':
                chapter_memberships = chapter_memberships.filter(
                                    approve_dt__year=start_dt.year,
                                    approve_dt__month=start_dt.month,
                                    approve_dt__day=start_dt.day,
                                    approved=True)
                if self.notice_type == 'approve':
                    chapter_memberships = chapter_memberships.filter(renewal=False)
                else:
                    chapter_memberships = chapter_memberships.filter(renewal=True)
            else:
                # notice_type == 'expiration'
                chapter_memberships = chapter_memberships.filter(
                                    expire_dt__year=start_dt.year,
                                    expire_dt__month=start_dt.month,
                                    expire_dt__day=start_dt.day,)


            # filter by chapter membership type
            if self.membership_type:
                chapter_memberships = chapter_memberships.filter(
                                membership_type=self.membership_type)
            if self.chapter:
                chapter_memberships = chapter_memberships.filter(
                                chapter=self.chapter)

            memberships_count = chapter_memberships.count()
        else:
            # notice_time == 'attimeof'
            if not chapter_membership:
                return
            chapter_memberships = [chapter_membership]
            memberships_count = 1

        if memberships_count > 0:
            # log notice sent
            notice_log = NoticeLog(notice=self,
                                   num_sent=0)
            notice_log.save()
            self.log = notice_log

            for chapter_membership in chapter_memberships:
                try:
                    boo_sent = self.email_chapter_member(chapter_membership, verbosity=verbosity)
                    if boo_sent:
                        num_sent += 1
                        if memberships_count <= 50:
                            self.chapter_memberships_processed.append(chapter_membership)

                        # log record
                        notice_log_record = NoticeDefaultLogRecord(
                                                notice_log=notice_log,
                                                chapter_membership=chapter_membership,
                                                emails_sent=chapter_membership.user.email)
                        notice_log_record.save()
                except:
                    # log the exception
                    logger.error(traceback.format_exc())

            if num_sent > 0:
                notice_log.num_sent = num_sent
                notice_log.save()

        return num_sent

    @classmethod
    def send_notices(cls, **kwargs):
        """
        Send auto responder notices with notice_type specified
        and chapter membership specified
        Returns boolean.

        Example:

          notice_sent =  Notice.send_notices(
                            notice_type='apply',
                            chapter_membership=chapter_membership,
                            membership_type=chapter_membership.membership_type,
                        )
        """

        notice_type = kwargs.get('notice_type') or 'apply'
        membership_type = kwargs.get('membership_type')
        chapter_membership = kwargs.get('chapter_membership')

        if not membership_type:
            return False

        if not isinstance(chapter_membership, ChapterMembership):
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
            chapter_requirments = (
                notice.chapter == chapter_membership.chapter,
                not notice.chapter
            )

            if any(notice_requirments) and any(chapter_requirments):
                notice.process_notice(chapter_membership=chapter_membership)

        return True


class NoticeLog(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice = models.ForeignKey(Notice, related_name="logs", on_delete=models.CASCADE)
    notice_sent_dt = models.DateTimeField(auto_now_add=True)
    num_sent = models.IntegerField()

    class Meta:
        verbose_name = _("Notice Log")
        verbose_name_plural = _("Notice Logs")
        app_label = 'chapters'

    def __str__(self):
        sent_dt = self.notice_sent_dt.strftime("%m/%d/%y")
        return f'Log for {self.notice} ({sent_dt})'


class NoticeDefaultLogRecord(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice_log = models.ForeignKey(NoticeLog,
                                   related_name="default_log_records",
                                   on_delete=models.CASCADE)
    chapter_membership = models.ForeignKey("ChapterMembership",
                                      related_name="default_log_records",
                                      on_delete=models.CASCADE)
    emails_sent = models.CharField(max_length=500, default='')
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Notice Log Record")
        verbose_name_plural = _("Notice Log Records")
        app_label = 'chapters'


def get_import_file_path(instance, filename):
    return "imports/chapters/{uuid}/{filename}".format(
                            uuid=uuid.uuid4().hex[:8],
                            filename=filename)


class ChapterMembershipImport(BaseImport):
    chapter = models.ForeignKey(Chapter, null=True, on_delete=models.SET_NULL)
    upload_file = models.FileField(_("Upload File"), max_length=260,
                                   upload_to=get_import_file_path,
                                   null=True)
    recap_file = models.FileField(_("Recap File"), max_length=260,
                                   null=True)
    key = models.CharField(_('Key'), max_length=50, default='')

    class Meta:
        app_label = 'chapters'

    def get_total_number_of_rows(self):
        """
        Get the total number of rows.
        """
        total_num = 0
        if self.upload_file:
            read_obj = default_storage.open(self.upload_file.name, 'r')
            total_num = len(list(reader(read_obj))) - 1
            read_obj.close()

        return total_num

    def get_header_and_first_row(self):
        if self.upload_file:
            header_row = None
            first_row = None
            with default_storage.open(self.upload_file.name, 'r') as read_obj:
                csv_reader = reader(read_obj)
                header_row = next(csv_reader)
                if header_row != None:
                    for row in csv_reader:
                        first_row = row
                        break
        if header_row != None:
            header_row = [item.strip() for item in header_row]
        return header_row, first_row

    def generate_recap(self):
        if not self.recap_file and self.header_line:
            file_name = 'chapter_memberships_import_%d_recap.csv' % self.id
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
            data_list = ChapterMembershipImportData.objects.filter(
                mimport=self).order_by('row_num')
            for idata in data_list:
                data_dict = idata.row_data
                row = [data_dict[k] for k in header_row if k in data_dict]
                row.extend([idata.action_taken, idata.error])
                recap_writer.writerow(row)

            f.close()
            self.recap_file.name = file_path
            self.save()


class ChapterMembershipImportData(BaseImportData):
    mimport = models.ForeignKey(ChapterMembershipImport, related_name="import_data", on_delete=models.CASCADE)

    class Meta:
        app_label = 'chapters'
