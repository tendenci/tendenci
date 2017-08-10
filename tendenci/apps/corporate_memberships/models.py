import operator
import time
import uuid
from datetime import datetime, timedelta
from functools import partial

from django import forms
from importlib import import_module
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template import Context, Template
from django.template.loader import render_to_string
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete

#from django.contrib.contenttypes.models import ContentType
from tendenci.libs.tinymce import models as tinymce_models

#from completion import AutocompleteProvider, site
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.memberships.models import (MembershipType,
                                                MembershipApp,
                                                MembershipDefault)
from tendenci.apps.forms_builder.forms.settings import (FIELD_MAX_LENGTH,
                                                        LABEL_MAX_LENGTH)
from tendenci.apps.corporate_memberships.managers import (
                                                CorpMembershipManager,
                                                CorpMembershipAppManager)
#from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import GroupMembership
from tendenci.apps.payments.models import PaymentMethod, Payment
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.profiles.models import Profile
from tendenci.apps.base.fields import DictField, CountrySelectField

from tendenci.apps.notifications import models as notification
from tendenci.apps.base.utils import send_email_notification, fieldify, get_salesforce_access
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.corporate_memberships.utils import (
                                            corp_membership_update_perms,
                                            dues_rep_emails_list,
                                            create_salesforce_lead)
from tendenci.apps.imports.utils import get_unique_username
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.industries.models import Industry
from tendenci.apps.regions.models import Region
from tendenci.apps.events.models import Event, Registrant
from tendenci.apps.base.utils import truncate_words
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.files.models import File
from functools import reduce


FIELD_CHOICES = (
                    ("CharField", _("Text")),
                    ("CharField/django.forms.Textarea", _("Paragraph Text")),
                    ("BooleanField", _("Checkbox")),
                    ("ChoiceField", _("Select One from a list (Drop Down)")),
                    ("ChoiceField/django.forms.RadioSelect",
                        _("Select One from a list (Radio Buttons)")),
                    ("MultipleChoiceField", _("Multi select (Drop Down)")),
                    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple",
                        _("Multi select (Checkboxes)")),
                    ("EmailField", _("Email")),
                    ("FileField", _("File upload")),
                    ("DateField/django.forms.extras.SelectDateWidget",
                        _("Date")),
                    ("DateTimeField", _("Date/time")),
                    ("section_break", _("Section Break")),
                    ("page_break", _("Page Break")),
                )

FIELD_LAYOUT_CHOICES = (
                        ('1', _('One Column')),
                        ('2', _('Two Columns')),
                        ('3', _('Three Columns')),
                        ('0', _('Side by Side')),
                        )
AUTH_METHOD_CHOICES = (
                       ('admin', _('Admin Approval')),
                       ('email', _('E-mail Domain')),
                       ('secret_code', _('Secret Code')),
                       )
SIZE_CHOICES = (
                ('s', _('Small')),
                ('m', _('Medium')),
                ('l', _('Large')),
                )
NOTICE_TYPES = (
    ('approve_join', _('Approval Date')),
    ('disapprove_join', _('Disapproval Date')),
    ('approve_renewal', _('Renewal Approval Date')),
    ('disapprove_renewal', _('Renewal Disapproval Date')),
    ('expiration', _('Expiration Date')),
)


class CorporateMembershipType(OrderingBaseModel, TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.CharField(_('Description'), max_length=500)
    price = models.DecimalField(_('Price'), max_digits=15, decimal_places=2,
                                blank=True, default=0,
                                help_text=_("Set 0 for free membership."))
    renewal_price = models.DecimalField(_('Renewal Price'), max_digits=15,
                                        decimal_places=2,
                                        blank=True, default=0, null=True,
                                        help_text=_("Set 0 for free membership."))
    membership_type = models.ForeignKey(MembershipType,
        help_text=_("Bind individual memberships to this membership type."))
    admin_only = models.BooleanField(_('Admin Only'), default=False)

    apply_cap = models.BooleanField(_('Apply cap'),
                                    help_text=_('If checked, specify the membership cap below.'),
                                    default=False)
    membership_cap = models.IntegerField(_('Membership cap'),
                                               default=0,
                                               blank=True,
                                               null=True,
                                               help_text=_('The maximum number of employees allowed.'))
    allow_above_cap = models.BooleanField(_('Allow above cap'),
                                    help_text=_('If Apply cap is checked, check this box to allow additional members to join above cap.'),
                                    default=False)
    above_cap_price = models.DecimalField(_('Price if join above cap'), max_digits=15,
                                          decimal_places=2,
                                          default=0,
                                          blank=True,
                                          null=True,
                                          help_text=_('Price for members who join above cap.'))
                                
    number_passes = models.PositiveIntegerField(_('Number Passes'),
                                               default=0,
                                               blank=True)


    class Meta:
        app_label = 'corporate_memberships'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(CorporateMembershipType, self).save(*args, **kwargs)

    def get_expiration_dt(self, renewal=False, join_dt=None, renew_dt=None, previous_expire_dt=None):
        """
        Calculate the expiration date - for join or renew (renewal=True)
        Examples:
            For join:
                expiration_dt = corporate_membership_type.get_expiration_dt(
                                    join_dt=membership.join_dt)
            For renew:
                expiration_dt = corporate_membership_type.get_expiration_dt(
                                        renewal=1,
                                        join_dt=membership.join_dt,
                                        renew_dt=membership.renew_dt)
        """
        return self.membership_type.get_expiration_dt(renewal=renewal, join_dt=join_dt, renew_dt=renew_dt, previous_expire_dt=previous_expire_dt)


class CorpProfile(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    logo = models.ForeignKey(File, null=True)
    name = models.CharField(max_length=250, unique=True)
    address = models.CharField(_('Address'), max_length=150,
                               blank=True, default='')
    address2 = models.CharField(_('Address2'), max_length=100, default='',
                                blank=True)
    city = models.CharField(_('City'), max_length=50, blank=True, default='')
    state = models.CharField(_('State'), max_length=50, blank=True,
                             default='')
    zip = models.CharField(_('Zipcode'), max_length=50,
                           blank=True, default='')
    country = models.CharField(_('Country'), max_length=50,
                               blank=True, default='')
    phone = models.CharField(_('Phone'), max_length=50,
                             blank=True, default='')
    email = models.CharField(_('Email'), max_length=200,
                             blank=True, default='')
    url = models.CharField(_('URL'), max_length=100, blank=True,
                           default='')
    secret_code = models.CharField(max_length=50, blank=True,
                                   default='')

    industry = models.ForeignKey(Industry, blank=True, null=True)
    region = models.ForeignKey(Region, blank=True, null=True)
    number_employees = models.IntegerField(default=0)
    chapter = models.CharField(_('Chapter'), max_length=150,
                               blank=True, default='')
    tax_exempt = models.BooleanField(_("Tax exempt"), default=False)

    annual_revenue = models.CharField(_('Annual revenue'), max_length=75,
                               blank=True, default='')
    annual_ad_expenditure = models.CharField(max_length=75,
                               blank=True, default='')
    description = models.TextField(blank=True, default='')
    expectations = models.TextField(blank=True, default='')
    notes = models.TextField(_('Notes'),
                               blank=True, default='')

    referral_source = models.CharField(max_length=150,
                             blank=True, default='')
    referral_source_other = models.CharField(max_length=150,
                             blank=True, default='')
    referral_source_member_name = models.CharField(max_length=50,
                             blank=True, default='')
    referral_source_member_number = models.CharField(max_length=50,
                             blank=True, default='')

    ud1 = models.TextField(blank=True, default='', null=True)
    ud2 = models.TextField(blank=True, default='', null=True)
    ud3 = models.TextField(blank=True, default='', null=True)
    ud4 = models.TextField(blank=True, default='', null=True)
    ud5 = models.TextField(blank=True, default='', null=True)
    ud6 = models.TextField(blank=True, default='', null=True)
    ud7 = models.TextField(blank=True, default='', null=True)
    ud8 = models.TextField(blank=True, default='', null=True)

    perms = GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")

    class Meta:
        app_label = 'corporate_memberships'

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid1())
        if not self.entity:
                self.entity_id = 1
        super(CorpProfile, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % (self.name)

    def assign_secret_code(self):
        if not self.secret_code:
            # use the make_random_password in the User object
            length = 6
            allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEF' + \
                            'GHJKLMNPQRSTUVWXYZ23456789'
            secret_code = User.objects.make_random_password(
                                                length=length,
                                                allowed_chars=allowed_chars)
            # check if this one is unique
            corp_profiles = CorpProfile.objects.filter(
                                            secret_code=secret_code)

            while corp_profiles:
                secret_code = User.objects.make_random_password(
                                            length=length,
                                            allowed_chars=allowed_chars)
                corp_profiles = CorpProfile.objects.filter(
                                                secret_code=secret_code)
                if not corp_profiles:
                    break
            self.secret_code = secret_code

    @property
    def active_corp_membership(self):
        [corp_membership] = self.corp_memberships.filter(
                                            status=True,
                                            status_detail='active'
                                            ).order_by(
                                            '-expiration_dt'
                                            )[:1] or [None]
        return corp_membership

    @property
    def corp_membership(self):
        [corp_membership] = self.corp_memberships.filter(
                                            status=True
                                            ).exclude(
                                            status_detail='archive'
                                            ).order_by(
                                            '-expiration_dt'
                                            )[:1] or [None]
        return corp_membership

    def is_rep(self, this_user):
        """
        Check if this user is one of the representatives of
        # this corp profile.
        """
        if this_user.is_anonymous():
            return False
        reps = self.reps.all()
        for rep in reps:
            if rep.user.id == this_user.id:
                return True
        return False
    
    def get_logo_url(self):
        if not self.logo:
            return u''

        return reverse('file', args=[self.logo.pk])


class CorpMembership(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    corp_profile = models.ForeignKey("CorpProfile",
                                     related_name='corp_memberships')
    corporate_membership_type = models.ForeignKey("CorporateMembershipType",
                                    verbose_name=_("MembershipType"))
    renewal = models.BooleanField(default=False)
    renew_from_id = models.IntegerField(blank=True, null=True)
    renew_dt = models.DateTimeField(_("Renew Date Time"), null=True)
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    join_dt = models.DateTimeField(_("Join Date Time"))
    expiration_dt = models.DateTimeField(_("Expiration Date Time"),
                                         blank=True, null=True)
    approved = models.BooleanField(_("Approved"), default=False)
    approved_denied_dt = models.DateTimeField(_(
                                        "Approved or Denied Date Time"),
                                              null=True)
    approved_denied_user = models.ForeignKey(User,
                                     verbose_name=_("Approved or Denied User"),
                                     null=True)
    payment_method = models.ForeignKey(PaymentMethod,
                                       verbose_name=_("Payment Method"),
                                       null=True, default=None)

    invoice = models.ForeignKey(Invoice, blank=True, null=True)

    anonymous_creator = models.ForeignKey('Creator', null=True)
    admin_notes = models.TextField(_('Admin notes'),
                               blank=True, null=True)
    total_passes_allowed = models.PositiveIntegerField(_('Total Passes Allowed'),
                                               default=0,
                                               blank=True)

    perms = GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")

    objects = CorpMembershipManager()
    VALID_STATUS_DETAIL = ['active',
                           'pending',
                           'paid - pending approval',
                           'expired',
                           'archive',
                           'inactive']

    class Meta:
        permissions = (("view_corpmembership", "Can view corporate membership"),)
        if get_setting('module', 'corporate_memberships', 'label'):
            verbose_name = get_setting('module',
                                       'corporate_memberships',
                                       'label')
            verbose_name_plural = get_setting('module',
                                              'corporate_memberships',
                                              'label_plural')
        else:
            verbose_name = _("Corporate Member")
            verbose_name_plural = _("Corporate Members")
        app_label = 'corporate_memberships'

    def __unicode__(self):
        return "%s" % (self.corp_profile.name)

    @models.permalink
    def get_absolute_url(self):
        """
        Returns admin change_form page.
        """
        return ('corpmembership.view', [self.pk])

    @property
    def group(self):
        return self.corporate_membership_type.membership_type.group

    @property
    def membership_type(self):
        return self.corporate_membership_type.membership_type

    @models.permalink
    def get_renewal_url(self):
        """
        Returns admin change_form page.
        """
        return ('corpmembership.renew', [self.pk])

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid1())
        if not self.entity:
                self.entity_id = 1
        self.allow_anonymous_view = False
        super(CorpMembership, self).save(*args, **kwargs)

    @property
    def module_name(self):
        return self._meta.model_name

    @property
    def free_pass_used(self):
        return self.passes_used.count()

    @property
    def free_pass_total(self):
        return self.total_passes_allowed

    @property
    def free_pass_avail(self):
        total = self.free_pass_total
        if not total:
            return 0
        return total - self.free_pass_used

    @property
    def authentication_method(self):
        app = CorpMembershipApp.objects.current_app()
        if app:
            return app.authentication_method
        return None

    def get_field_value(self, field_name):
        if field_name:
            if hasattr(self, field_name):
                return getattr(self, field_name)
            if hasattr(self.corp_profile, field_name):
                return getattr(self.corp_profile, field_name)
            if field_name == 'authorized_domain':
                auth_domains = self.corp_profile.authorized_domains.all()
                return ', '.join([domain.name for domain in auth_domains])
        return ''

    def get_labels(self):
        corp_app = CorpMembershipApp.objects.current_app()
        return dict(CorpMembershipAppField.objects.filter(
                corp_app=corp_app
                ).values_list('field_name', 'label'
                ).exclude(field_name=''))

    @staticmethod
    def get_search_filter(user, my_corps_only=False):
        filter_and, filter_or = None, None
        if my_corps_only:
            filter_or = ({'creator': user,
                         'owner': user,
                         'corp_profile__reps__user': user})
            if user.profile.is_superuser:
                filter_and = {'status': True,
                          'status_detail': 'active'}
        else:
            if user.profile.is_superuser or  has_perm(user, 'corporate_memberships.view_corpmembership'):
                return None, None

            allow_anonymous_search = get_setting('module',
                                         'corporate_memberships',
                                         'anonymoussearchcorporatemembers')
            allow_member_search = get_setting('module',
                                      'corporate_memberships',
                                      'membersearchcorporatemembers')

            if allow_anonymous_search or \
                (allow_member_search and user.profile.is_member):
                filter_and = {'status': True,
                              'status_detail': 'active'}
            else:
                if user.is_authenticated():
                    filter_or = {'creator': user,
                                 'owner': user}
                    filter_or.update({'corp_profile__reps__user': user})
                else:
                    filter_and = {'allow_anonymous_view': True}

        return filter_and, filter_or

    @staticmethod
    def get_membership_search_filter(user):
        if user.profile.is_superuser:
            return None, None

        filter_or = None
        filter_and = {'status': True,
                      'status_detail': 'active'}
        if not user.is_anonymous():
            if user.profile.is_member:
                filter_or = {'allow_anonymous_view': True,
                             'allow_user_view': True,
                             'allow_member_view': True}
            else:
                filter_or = {'allow_anonymous_view': True,
                             'allow_user_view': True}
            filter_or.update({'creator': user,
                             'owner': user})
        else:
            filter_and = {'allow_anonymous_view': True}

        return filter_and, filter_or

    @staticmethod
    def get_my_corporate_memberships(user, my_corps_only=False):
        """Get the corporate memberships owned or has the permission
            by this user.
            Returns a query set.
        """
        if not my_corps_only and user.profile.is_superuser:
            return CorpMembership.objects.all()

        filter_and, filter_or = CorpMembership.get_search_filter(user,
                                            my_corps_only=my_corps_only)
        q_obj = None
        if filter_and:
            q_obj = Q(**filter_and)
        if filter_or:
            q_obj_or = reduce(operator.or_, [Q(**{key: value}
                        ) for key, value in filter_or.items()])
            if q_obj:
                q_obj = reduce(operator.and_, [q_obj, q_obj_or])
            else:
                q_obj = q_obj_or
        if q_obj:
            return CorpMembership.objects.filter(q_obj)
        else:
            return CorpMembership.objects.all()

    @staticmethod
    def get_my_corporate_profiles_choices(user):
        corp_members = CorpMembership.get_my_corporate_memberships(user)
        corp_members = corp_members.exclude(status_detail='archive')
        if not user.profile.is_superuser:
            corp_members = corp_members.filter(status_detail__in=['active',
                                                                  'expired'])
        corp_members = corp_members.values_list(
                        'id', 'corp_profile__name'
                                ).order_by('corp_profile__name')
        choices = [(0, _('Select One'))]
        choices.extend([
                        (value[0], truncate_words(value[1], 10)) for value in corp_members
                                              ])
        return choices


    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed
        on invoice.
        If not supplied, the default description will be generated.
        """
        return 'Tendenci Invoice %d for Corp. Memb. (%d): %s. ' % (
            inv.id,
            inv.object_id,
            self,
        )

    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the corporate membership sale
        """
        from tendenci.apps.accountings.models import Acct, AcctEntry, AcctTran
        from tendenci.apps.accountings.utils import (make_acct_entries_initial,
                                                     make_acct_entries_closing)

        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)

            # #CREDIT corporate membership SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount*(-1))

    def get_acct_number(self, discount=False):
        if discount:
            return 466800
        else:
            return 406800

    def get_field_items(self):
        app = CorpMembershipApp.objects.current_app()
        # to be updated if supports multiple apps
        # app = self.app
        items = {}
        field_names = CorpMembershipAppField.objects.filter(
                                        corp_app=app,
                                        display=True,
                                        ).exclude(
                                        field_name=''
                                        ).values_list('field_name',
                                                      flat=True)
        if field_names:
            profile = self.corp_profile
            for field_name in field_names:
                if hasattr(profile, field_name):
                    items[field_name] = getattr(profile, field_name)
                elif hasattr(self, field_name):
                    items[field_name] = getattr(self, field_name)

            for name, value in items.iteritems():
                if hasattr(value, 'all'):
                    items[name] = ', '.join([item.__unicode__() \
                                             for item in value.all()])
        return items

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """
        try:
            from tendenci.apps.notifications import models as notification
        except:
            notification = None
        from tendenci.apps.perms.utils import get_notice_recipients

        # approve it
        if self.renewal:
            self.approve_renewal(request)
        else:
            params = {'create_new': False,
                      'assign_to_user': None}
            if self.anonymous_creator:
                [assign_to_user] = User.objects.filter(
                            first_name=self.anonymous_creator.first_name,
                            last_name=self.anonymous_creator.last_name,
                            email=self.anonymous_creator.email
                                )[:1] or [None]
                if assign_to_user:
                    params['assign_to_user'] = assign_to_user
                    params['create_new'] = False
                else:
                    params['create_new'] = True

            self.approve_join(request, **params)

        # send notification to administrators
        recipients = get_notice_recipients('module',
                                           'corporate_memberships',
                                           'corporatemembershiprecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': self,
                    'request': request,
                }
                notification.send_emails(recipients,
                                         'corp_memb_paid',
                                         extra_context)

    def get_payment_method(self, is_online=True):
        # return payment method if defined
        if self.payment_method:
            return self.payment_method

        # first method is credit card (online)
        # will raise exception if payment method does not exist
        [self.payment_method] = PaymentMethod.objects.filter(
                                is_online=is_online)[:1] or [None]

        return self.payment_method

    def copy(self):
        corp_membership = self.__class__()
        field_names = [field.name for field in self.__class__._meta.fields]
        ignore_fields = ['id', 'renewal', 'renew_dt', 'status',
                         'status_detail', 'approved', 'approved_denied_dt',
                         'approved_denied_user', 'anonymous_creator']
        for field in ignore_fields:
            field_names.remove(field)

        for name in field_names:
            setattr(corp_membership, name, getattr(self, name))
        return corp_membership

    def archive_old(self):
        """
        Archive the old records
        """
        corp_memberships = self.corp_profile.corp_memberships.exclude(
                                    id=self.id
                                        )
        for corp_memb in corp_memberships:
            corp_memb.status_detail = 'archive'
            corp_memb.save()

    def mark_invoice_as_paid(self, user):
        if self.invoice and not self.invoice.is_tendered:
            self.invoice.tender(user)  # tendered the invoice for admin if offline

            # mark payment as made
            payment = Payment()
            payment.payments_pop_by_invoice_user(user,
                        self.invoice, self.invoice.guid)
            payment.mark_as_paid()
            payment_method = self.get_payment_method()
            payment.method = payment_method and payment_method.machine_name or ''
            payment.save(user)

            # this will make accounting entry
            self.invoice.make_payment(user, payment.amount)

    def expire(self, request_user):
        """
        Expire this corporate memberships and its associated
        individual memberships.
        """
        if self.status and \
            self.status_detail == 'active' and \
            self.approved:
            self.status_detail = 'expired'
            self.expiration_dt = datetime.now()
            self.save()

            memberships = MembershipDefault.objects.filter(
                        corporate_membership_id=self.id
                            )
            for membership in memberships:
                membership.expire(request_user)
            return True
        return False

    def approve_join(self, request, **kwargs):
        self.approved = True
        self.approved_denied_dt = datetime.now()
        if not request.user.is_anonymous():
            self.approved_denied_user = request.user
        self.status = True
        self.status_detail = 'active'
        self.save()
        # mark invoice as paid
        self.mark_invoice_as_paid(request.user)

        created, username, password = self.handle_anonymous_creator(**kwargs)

        # create salesforce lead if applicable
        sf = get_salesforce_access()
        if sf:
            create_salesforce_lead(sf, self.corp_profile)

        if Notice.objects.filter(notice_time='attimeof',
                                 notice_type='approve_join',
                                 status=True,
                                 status_detail='active'
                                 ).exists():

            if self.anonymous_creator:
                login_url = '%s%s' % (
                        get_setting('site', 'global', 'siteurl'),
                        reverse('auth_login'))
                login_info = \
                render_to_string(
                    'notification/corp_memb_notice_email/join_login_info.html',
                    {'corp_membership': self,
                     'created': created,
                     'username': username,
                     'password': password,
                     'login_url': login_url,
                     'request': request})
            else:
                login_info = ''

            self.send_notice_email(request, 'approve_join',
                                anonymous_join_login_info=login_info)
        else:
            # send an email to dues reps
            recipients = dues_rep_emails_list(self)
            recipients.append(self.creator.email)
            extra_context = {
                'object': self,
                'request': request,
                'invoice': self.invoice,
                'created': created,
                'username': username,
                'password': password
            }
            send_email_notification('corp_memb_join_approved',
                                recipients, extra_context)

    def disapprove_join(self, request, **kwargs):
        self.approved = False
        self.approved_denied_dt = datetime.now()
        self.approved_denied_user = request.user
        self.status = True
        self.status_detail = 'inactive'
        self.admin_notes = 'Disapproved by %s on %s. %s' % (
                                    request.user,
                                    self.approved_denied_dt,
                                    self.admin_notes
                                    )
        self.save()
        self.send_notice_email(request, 'disapprove_join')

    def approve_renewal(self, request, **kwargs):
        """
        Approve the corporate membership renewal, and
        approve the individual memberships that are
        renewed with the corporate_membership
        """
        if self.renewal and self.status_detail in [
                        'pending', 'paid - pending approval']:
            request_user = request.user
            # 2) approve corp_membership
            self.approved = True
            self.approved_denied_dt = datetime.now()
            if request_user and (not request_user.is_anonymous()):
                self.approved_denied_user = request_user
            self.status = True
            self.status_detail = 'active'
            # calculate the expiration date
            if self.renew_from_id:
                [previous_expire_dt] = CorpMembership.objects.filter(
                                            id=self.renew_from_id).values_list(
                                            'expiration_dt', flat=True)[:1] or [None]
            else:
                previous_expire_dt = None
            corp_memb_type = self.corporate_membership_type
            self.expiration_dt = corp_memb_type.get_expiration_dt(
                                            renewal=True,
                                            join_dt=self.join_dt,
                                            renew_dt=self.renew_dt,
                                            previous_expire_dt=previous_expire_dt)
            if not request_user.is_anonymous():
                self.owner = request_user
                self.owner_username = request_user.username
            self.save()

            # 2) approve the individual memberships
            group = self.corporate_membership_type.membership_type.group

            ind_memb_renew_entries = IndivMembershipRenewEntry.objects.filter(
                                            corp_membership=self)
            total_individuals_renewed = ind_memb_renew_entries.count()
            for memb_entry in ind_memb_renew_entries:
                membership = memb_entry.membership
                new_membership = membership.copy()
                # update the membership record with the renewal info
                new_membership.renewal = True
                new_membership.renew_dt = self.renew_dt
                new_membership.expire_dt = self.expiration_dt
                new_membership.corporate_membership_id = self.id
                new_membership.corp_profile_id = self.corp_profile.id
                new_membership.membership_type = \
                    self.corporate_membership_type.membership_type
                new_membership.status = True
                new_membership.status_detail = 'active'
                new_membership.application_approved = True
                new_membership.application_approved_dt = self.approved_denied_dt
                if not request_user.is_anonymous():
                    new_membership.owner_id = request_user.id
                    new_membership.owner_username = request_user.username
                    new_membership.application_approved_user = request_user

                new_membership.save()
                # archive old memberships
                new_membership.archive_old_memberships()
                
                # show member_number on profile
                new_membership.profile_refresh_member_number()

                # check and add member to the group if not exist
                [gm] = GroupMembership.objects.filter(group=group,
                                                    member=new_membership.user
                                                    )[:1] or [None]
                if gm:
                    if gm.status_detail != 'active':
                        gm.status_detail = 'active'
                        gm.save()
                else:
                    opt = {
                        'group': group,
                        'member': new_membership.user,
                        'status': True,
                        'status_detail': 'active',
                        }
                    if not request_user.is_anonymous():
                        opt.update({
                                'creator_id': request_user.id,
                                'creator_username': request_user.username,
                                'owner_id': request_user.id,
                                'owner_username': request_user.username,
                                   })
                    GroupMembership.objects.create(**opt)

                # update the status_detail for memb_entry
                memb_entry.status_detail = 'approved'
                memb_entry.save()

            # mark invoice as paid
            self.mark_invoice_as_paid(request.user)

            if Notice.objects.filter(notice_time='attimeof',
                                 notice_type='approve_renewal',
                                 status=True,
                                 status_detail='active'
                                 ).exists():
                self.send_notice_email(request, 'approve_renewal')
            else:
                # email dues reps that corporate membership has been approved
                recipients = dues_rep_emails_list(self)
                if not recipients and self.creator:
                    recipients = [self.creator.email]
                extra_context = {
                    'object': self,
                    'request': request,
                    'invoice': self.invoice,
                    'total_individuals_renewed': total_individuals_renewed
                }
                send_email_notification('corp_memb_renewal_approved',
                                        recipients, extra_context)

    def disapprove_renewal(self, request, **kwargs):
        """
        deny the corporate membership renewal
        set the status detail to 'disapproved'
        """
        if self.renewal and self.status_detail in [
                        'pending', 'paid - pending approval']:
            request_user = request.user
            self.approved = True
            self.approved_denied_dt = datetime.now()
            self.status_detail = 'inactive'
            if not request_user.is_anonymous():
                self.owner = request_user
                self.owner_username = request_user.username
            self.save()

            self.send_notice_email(request, 'disapprove_renewal')

        ind_memb_renew_entries = IndivMembershipRenewEntry.objects.filter(
                                            corp_membership=self)
        for memb_entry in ind_memb_renew_entries:
            memb_entry.status_detail = 'disapproved'
            memb_entry.save()

    def handle_anonymous_creator(self, **kwargs):
        """
        Handle the anonymous creator on approval and disapproval.
        """
        if self.anonymous_creator:
            create_new = kwargs.get('create_new', False)
            assign_to_user = kwargs.get('assign_to_user', None)

            params = {'first_name': self.anonymous_creator.first_name,
                      'last_name': self.anonymous_creator.last_name,
                      'email': self.anonymous_creator.email}

            if assign_to_user and not isinstance(assign_to_user, User):
                create_new = True

            if not create_new and not assign_to_user:

                [my_user] = User.objects.filter(**params).order_by(
                                        '-is_active')[:1] or [None]
                if my_user:
                    assign_to_user = my_user
                else:
                    create_new = True
            if create_new:
                params.update({
                   'password': User.objects.make_random_password(length=8),
                   'is_active': True})
                assign_to_user = User(**params)
                assign_to_user.username = get_unique_username(assign_to_user)
                assign_to_user.set_password(assign_to_user.password)
                assign_to_user.save()

                # create a profile for this new user
                Profile.objects.create_profile(assign_to_user)

            self.creator = assign_to_user
            self.creator_username = assign_to_user.username
            self.owner = assign_to_user
            self.owner_username = assign_to_user.username
            self.save()

            # assign creator to be dues_rep
            if not CorpMembershipRep.objects.filter(
                                    corp_profile=self.corp_profile,
                                    user=self.creator).exists():
                CorpMembershipRep.objects.create(
                        corp_profile=self.corp_profile,
                        user=self.creator,
                        is_dues_rep=True
                                )

            corp_membership_update_perms(self)

            # update invoice creator/owner
            if self.invoice:
                self.invoice.creator = assign_to_user
                self.invoice.creator_username = assign_to_user.username
                self.invoice.owner = assign_to_user
                self.invoice.owner_username = assign_to_user.username
                self.invoice.save()

            return create_new, assign_to_user.username, params.get('password',
                                                                   '')

        return False, None, None

    def is_rep(self, this_user):
        """
        Check if this user is one of the representatives of
        this corporate membership.
        """
        return self.corp_profile.is_rep(this_user)

    def allow_view_by(self, this_user):
        if this_user.profile.is_superuser:
            return True

        if get_setting('module',
                     'corporate_memberships',
                     'anonymoussearchcorporatemembers'):
            return True

        if not this_user.is_anonymous():
            if self.is_rep(this_user):
                return True
            if self.creator:
                if this_user.id == self.creator.id:
                    return True
            if self.owner:
                if this_user.id == self.owner.id:
                    return True

        return False

    def allow_edit_by(self, this_user):
        if self.is_active or self.is_expired:
            if this_user.profile.is_superuser:
                return True
            if has_perm(this_user, 'corporate_memberships.change_corpmembership'):
                return True

            if not this_user.is_anonymous():
                if self.is_active:
                    if self.is_rep(this_user):
                        return True
                    if self.creator:
                        if this_user.id == self.creator.id:
                            return True
                    if self.owner:
                        if this_user.id == self.owner.id:
                            return True

        return False

    def get_renewal_period_dt(self):
        """
        calculate and return a tuple of renewal period dt:
         (renewal_period_start_dt, renewal_period_end_dt)
        """
        if not self.expiration_dt or not isinstance(self.expiration_dt, datetime):
            return (None, None)
        membership_type = self.corporate_membership_type.membership_type
        start_dt = self.expiration_dt - timedelta(
                            days=membership_type.renewal_period_start)
        end_dt = self.expiration_dt + timedelta(
                            days=membership_type.renewal_period_end)

        return (start_dt, end_dt)

    def can_renew(self):
        if self.status_detail == 'archive':
            return False
        if not self.expiration_dt or not isinstance(self.expiration_dt,
                                                    datetime):
            return False

        (renewal_period_start_dt,
         renewal_period_end_dt) = self.get_renewal_period_dt()

        now = datetime.now()
        return (now >= renewal_period_start_dt and now <= renewal_period_end_dt)

    def send_notice_email(self, request, notice_type, **kwargs):
        """
        Convenience method for sending
            typical corporate membership emails.
        Returns outcome via boolean.
        """
        representatives = self.corp_profile.reps.filter(Q(is_dues_rep=True)|(Q(is_member_rep=True)))

        return Notice.send_notice(
            request=request,
            recipients=representatives,
            notice_type=notice_type,
            corporate_membership=self,
            corporate_membership_type=self.corporate_membership_type,
            **kwargs
        )

    @property
    def is_join_pending(self):
        return not self.renewal and self.status_detail in [
                                    'pending',
                                    'paid - pending approval']

    @property
    def is_renewal_pending(self):
        return self.renewal and self.status_detail in [
                            'pending',
                            'paid - pending approval']

    @property
    def is_pending(self):
        return self.status_detail in [
                            'pending',
                            'paid - pending approval']

    @property
    def is_expired(self):
        if self.status_detail.lower() in ('active', 'expired'):
            if not self.expiration_dt or not isinstance(self.expiration_dt,
                                                        datetime):
                return False
            return datetime.now() >= self.expiration_dt
        return False

    @property
    def is_archive(self):
        return self.status_detail.lower() in ('archive',)
    
    def get_latest_renewed(self):
        """
        Get the latest renewed corpMembership.
        """
        if self.is_archive:
            [latest_renewed] = CorpMembership.objects.filter(
                                    corp_profile=self.corp_profile,
                                    expiration_dt__gt=self.expiration_dt,
                                    status_detail='active'
                                    ).order_by('-expiration_dt')[:1] or [None]
            return latest_renewed
            
        return None

    @property
    def is_in_grace_period(self):
        if self.is_expired:
            grace_period_end_dt = self.expiration_dt + timedelta(
                days=self.corporate_membership_type.membership_type.expiration_grace_period)

            return datetime.now() < grace_period_end_dt
        return False

    @property
    def real_time_status_detail(self):
        if self.is_expired:
            if self.is_in_grace_period:
                return "expired - in grace period"
            else:
                return "expired"
        else:
            return self.status_detail

    @property
    def is_active(self):
        return self.status_detail.lower() in ('active',)

    @property
    def obj_perms(self):
        t = '<span class="t-perm t-perm-%s">%s</span>'

        if get_setting('module', 'corporate_memberships', 'anonymoussearchcorporatemembers'):
            value = t % ('public', 'Public')
        else:
            value = t % ('private', 'Private')

        return mark_safe(value)

    @property
    def members_count(self):
        """
        Count of the individual members.
        """
        return MembershipDefault.objects.filter(
                        corp_profile_id=self.corp_profile.id,
                        status=True
                            ).exclude(
                        status_detail__in=['archive', 'expired']).count()

    def get_cap_info(self):
        """
        Return a tuple of (apply_cap, membership_cap)
        """
        corp_type = self.corporate_membership_type
        return (corp_type.apply_cap, corp_type.membership_cap, corp_type.allow_above_cap, corp_type.above_cap_price)

    def is_cap_reached(self, num_exclude=0):
        apply_cap, cap,  = self.get_cap_info()[:2]

        return apply_cap and self.members_count - num_exclude >= cap
    
    def get_above_cap_price(self, num_exclude=0):
        """
        get the above cap price for individual memberships.
        return tuple (apply_above_cap, above_cap_price)
        """
        corporate_type = self.corporate_membership_type
        if corporate_type.apply_cap and self.is_cap_reached(num_exclude=num_exclude):
            if corporate_type.allow_above_cap:
                return True, corporate_type.above_cap_price

        return False, None

    def email_reps_cap_reached(self):
        """
        Email corporate reps and admin about the cap has been reached.
        """
        from tendenci.apps.emails.models import Email
        # email to reps
        email_sent_to_reps = False
        reps = self.corp_profile.reps.all()
        email_context = {'corp_membership': self,
                         'corp_profile': self.corp_profile,
                         'corp_membership_type': self.corporate_membership_type,
                         'currency_symbol': get_setting('site', 'global', 'currencysymbol'),
                         'site_url': get_setting('site', 'global', 'siteurl'),
                         'site_display_name': get_setting('site', 'global', 'sitedisplayname'),
                         'view_link': self.get_absolute_url(),
                         'roster_link': "%s?cm_id=%s" % (reverse('corpmembership.roster_search'), self.id),
                         'upgrade_link': reverse('corpmembership.upgrade', args=[self.id])}
        membership_recipients = get_setting('module', 'memberships', 'membershiprecipients')
        
        if reps:
            email_context['to_reps'] =  True
            subject = render_to_string('notification/corp_memb_cap_reached/short.txt', email_context)
            subject = subject.strip('\n').strip('\r')
            body = render_to_string('notification/corp_memb_cap_reached/full.html', email_context)
            email = Email()
            email.subject = subject
            email.body = body
            email.recipient = [rep.user.email for rep in reps]
            email.reply_to = membership_recipients
            email.content_type = 'html'
            email.send()
            email_sent_to_reps = True
        
        # email to site admins
        if membership_recipients:
            email_context['to_reps'] =  False
            subject = render_to_string('notification/corp_memb_cap_reached/short.txt', email_context)
            subject = "Admin: " + subject.strip('\n').strip('\r')
            body = render_to_string('notification/corp_memb_cap_reached/full.html', email_context)
            email = Email()
            email.subject = subject
            email.body = body
            email.recipient = membership_recipients
            email.content_type = 'html'
            email.send()
        
        return email_sent_to_reps


class FreePassesStat(TendenciBaseModel):
    user = models.ForeignKey(User, null=True)
    corp_membership = models.ForeignKey("CorpMembership",
                                related_name="passes_used")
    event = models.ForeignKey(Event, related_name="passes_used")
    registrant = models.ForeignKey(Registrant, null=True)

    class Meta:
        app_label = 'corporate_memberships'
 
    def set_creator_owner(self, request_user):
        if request_user and not request_user.is_anonymous():
            self.creator = request_user
            self.owner = request_user
            self.creator_username = request_user.username
            self.owner_username = request_user.username


class CorpMembershipApp(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(_("URL Path"), max_length=155, unique=True)
    corp_memb_type = models.ManyToManyField("CorporateMembershipType",
                                            verbose_name=_("Corp. Memb. Type"))
    authentication_method = models.CharField(_("Authentication Method"),
                                             choices=AUTH_METHOD_CHOICES,
                                    default='admin', max_length=50,
                                    help_text=_('Define a method for ' + \
                                    'individuals to be bound to their' + \
                                    ' corporate memberships when signing up.'))
    description = tinymce_models.HTMLField(_("Description"),
                                    blank=True, null=True,
                                   help_text=_('Will display at the top of ' + \
                                   'the application form.'))
    notes = models.TextField(_("Notes"), blank=True, null=True,
                                   help_text=_('Notes for editor. ' + \
                                   'Will not display on the application form.'))
    confirmation_text = models.TextField(_("Confirmation Text"),
                                         blank=True, null=True)

    memb_app = models.OneToOneField(MembershipApp,
                            help_text=_("App for individual memberships."),
                            related_name='corp_app',
                            verbose_name=_("Membership Application"),
                            default=1)
    payment_methods = models.ManyToManyField(PaymentMethod,
                                             verbose_name="Payment Methods")
    include_tax = models.BooleanField(default=False)
    tax_rate = models.DecimalField(blank=True, max_digits=5, decimal_places=4, default=0,
                                   help_text=_('Example: 0.0825 for 8.25%.'))

    objects = CorpMembershipAppManager()

    class Meta:
        verbose_name = _("Corporate Membership Application")
        verbose_name_plural = _("Corporate Membership Applications")
        ordering = ('name',)
        app_label = 'corporate_memberships'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("corpmembership_app.preview", [self.slug])

    def is_current(self):
        """
        Check if this app is the current app.
        Corporate memberships do not support multiple apps.
        """
        current_app = CorpMembershipApp.objects.current_app()

        return current_app and current_app.id == self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(CorpMembershipApp, self).save(*args, **kwargs)

        if not self.memb_app.use_for_corp:
            self.memb_app.use_for_corp = True
            self.memb_app.save()

    def application_form_link(self):
        if self.is_current():
            return '<a href="%s">%s</a>' % (reverse('corpmembership.add'),
                                            self.slug)
        return '--'

    application_form_link.allow_tags = True


class CorpMembershipAppField(OrderingBaseModel):
    FIELD_TYPE_CHOICES1 = (
                    ("CharField", _("Text")),
                    ("CharField/django.forms.Textarea", _("Paragraph Text")),
                    ("BooleanField", _("Checkbox")),
                    ("ChoiceField", _("Select One from a list (Drop Down)")),
                    ("ChoiceField/django.forms.RadioSelect",
                        _("Select One from a list (Radio Buttons)")),
                    ("MultipleChoiceField", _("Multi select (Drop Down)")),
                    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple",
                        _("Multi select (Checkboxes)")),
                    ("CountrySelectField", _("Countries Drop Down")),
                    ("EmailField", _("Email")),
                    ("FileField", _("File upload")),
                    ("DateField/django.forms.extras.SelectDateWidget",
                        _("Date")),
                    ("DateTimeField", _("Date/time")),
                )
    FIELD_TYPE_CHOICES2 = (
                    ("section_break", _("Section Break")),
                )
    FIELD_TYPE_CHOICES = FIELD_TYPE_CHOICES1 + FIELD_TYPE_CHOICES2

    corp_app = models.ForeignKey("CorpMembershipApp", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    field_name = models.CharField(_("Field Name"), max_length=30, blank=True,
                                  default='')
    field_type = models.CharField(_("Field Type"), choices=FIELD_TYPE_CHOICES,
                                  max_length=80,
                                  blank=True, null=True,
                                  default='CharField')

    required = models.BooleanField(_("Required"), default=False)
    display = models.BooleanField(_("Show"), default=True)
    admin_only = models.BooleanField(_("Admin Only"), default=False)

    help_text = models.CharField(_("Help Text"),
                                 max_length=2000, blank=True, default='')
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
                    null=True,
                    help_text=_("Comma separated options where applicable"))
    # checkbox/radiobutton
    field_layout = models.CharField(_("Choice Field Layout"),
                                    choices=FIELD_LAYOUT_CHOICES,
                                    max_length=50, blank=True,
                                    null=True, default='1')
    size = models.CharField(_("Field Size"), choices=SIZE_CHOICES,
                            max_length=1,
                            blank=True, null=True, default='m')
    default_value = models.CharField(_("Default Value"),
                                     max_length=100, blank=True, default='')
    css_class = models.CharField(_("CSS Class Name"),
                                 max_length=50, blank=True, default='')
    description = models.TextField(_("Description"),
                                   max_length=200,
                                   blank=True,
                                   default='')

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        ordering = ('position',)
        app_label = 'corporate_memberships'

    def __unicode__(self):
        if self.field_name:
            return '%s (field name: %s)' % (self.label, self.field_name)
        return '%s' % self.label

    def app_link(self):
        return '<a href="%s">%s</a>' % (
                reverse('admin:corporate_memberships_corpmembershipapp_change',
                        args=[self.corp_app.id]),
                self.corp_app.id)

    app_link.allow_tags = True

    def get_field_class(self, initial=None):
        """
            Generate the form field class for this field.
        """
        if self.field_type and self.id:
            if "/" in self.field_type:
                field_class, field_widget = self.field_type.split("/")
            else:
                field_class, field_widget = self.field_type, None
            if field_class == 'TextField':
                field_class = 'CharField'
            if field_class == 'CountrySelectField':
                field_class = CountrySelectField
            else:
                if self.field_name in ['tax_exempt'] and not self.choices:
                    field_class = forms.BooleanField
                else:
                    field_class = getattr(forms, field_class)
            field_args = {"label": self.label,
                          "required": self.required,
                          'help_text': self.help_text}
            arg_names = field_class.__init__.__func__.__code__.co_varnames
            if initial:
                field_args['initial'] = initial
            else:
                if self.default_value:
                    field_args['initial'] = self.default_value
            if "max_length" in arg_names:
                field_args["max_length"] = FIELD_MAX_LENGTH
            if "choices" in arg_names:
                if self.field_name not in [
                            'corporate_membership_type',
                            'payment_method']:
                    if self.choices == 'yesno':
                        field_args["choices"] = ((1, _('Yes')), (0, _('No')),)
                    else:
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
                                FIELD_CHOICES]
        corp_profile_fields = dict([(field.name, field) \
                        for field in CorpProfile._meta.fields \
                        if field.get_internal_type() != 'AutoField'])
        fld = None
        field_type = 'CharField'

        if field_name in corp_profile_fields:
            fld = corp_profile_fields[field_name]
        if not fld:
            corp_memb_fields = dict([(field.name, field) \
                            for field in CorpMembership._meta.fields])

            if field_name in corp_memb_fields:
                fld = corp_memb_fields[field_name]

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


class CorpMembershipAuthDomain(models.Model):
    corp_profile = models.ForeignKey("CorpProfile",
                                        related_name="authorized_domains")
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'corporate_memberships'

class CorpMembershipRep(models.Model):
    corp_profile = models.ForeignKey("CorpProfile",
                                        related_name="reps")
    user = models.ForeignKey(User, verbose_name=_("Representative"),)
    is_dues_rep = models.BooleanField(_('is dues rep?'),
                                      default=True, blank=True)
    is_member_rep = models.BooleanField(_('is member rep?'),
                                    default=True, blank=True)

    class Meta:
        unique_together = (("corp_profile", "user"),)
        app_label = 'corporate_memberships'

    def __unicode__(self):
        return 'Rep: %s for "%s"' % (self.user, self.corp_profile.name)


class IndivEmailVerification(models.Model):
    guid = models.CharField(max_length=50)
    corp_profile = models.ForeignKey("CorpProfile")
    verified_email = models.CharField(_('email'), max_length=200)
    verified = models.BooleanField(default=False)
    verified_dt = models.DateTimeField(null=True)
    creator = models.ForeignKey(User,
                                related_name="corp_email_veri8n_creator",
                                null=True,
                                on_delete=models.SET_NULL)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User,
                                   related_name="corp_email_veri8n_updator",
                                   null=True,
                                   on_delete=models.SET_NULL)
    class Meta:
        app_label = 'corporate_memberships'

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(IndivEmailVerification, self).save(*args, **kwargs)


class IndivMembershipRenewEntry(models.Model):
    """
    Hold the individual memberships to be renewed with
    the corporate membership.
    """
    STATUS_DETAIL_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('disapproved', _('Disapproved')),
    )
    corp_membership = models.ForeignKey("CorpMembership")
    membership = models.ForeignKey(MembershipDefault)
    status_detail = models.CharField(max_length=50,
                                     choices=STATUS_DETAIL_CHOICES,
                                     default='pending')

    class Meta:
        app_label = 'corporate_memberships'


def get_import_file_path(instance, filename):
    return "imports/corpmemberships/{uuid}/{filename}".format(
                            uuid=uuid.uuid1().get_hex()[:8],
                            filename=filename)


class CorpMembershipImport(models.Model):
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

    upload_file = models.FileField(_("Upload File"), max_length=260,
                                   upload_to=get_import_file_path)
    # overwrite already existing fields if match
    override = models.IntegerField(choices=OVERRIDE_CHOICES, default=0)
    # uniqueness key
    key = models.CharField(_('Key'), max_length=50,
                           default="name")
    bind_members = models.BooleanField(
                _('Bind members to corporations by their company names'), default=False)

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
        app_label = 'corporate_memberships'

    def get_file(self):
        return self.upload_file

    def __unicode__(self):
        return self.get_file().file.name


class CorpMembershipImportData(models.Model):
    mimport = models.ForeignKey(CorpMembershipImport,
                                related_name="corp_membership_import_data",)
    # dictionary object representing a row in csv
    row_data = DictField(_('Row Data'))
    # the original row number in the uploaded csv file
    row_num = models.IntegerField(_('Row #'))
    # action_taken can be 'insert', 'update' or 'mixed'
    action_taken = models.CharField(_('Action Taken'),
                                    max_length=20, null=True)

    class Meta:
        app_label = 'corporate_memberships'


class Creator(models.Model):
    """
    An anonymous user can create a corporate membership.
    This table allows us to collect some contact info for admin
    to contact them.
    Once the corporate membership is approved, if not found in db,
    a user record will be created based on this info and will be
    associated to the corporate membership as creator and dues rep.
    """
    first_name = models.CharField(_('Contact first name') , max_length=30, blank=True)
    last_name = models.CharField(_('Contact last name') , max_length=30, blank=True)
    email = models.EmailField(_('Contact e-mail address'))
    hash = models.CharField(max_length=32, default='')

    class Meta:
        app_label = 'corporate_memberships'


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
    corporate_membership_type = models.ForeignKey(
        "CorporateMembershipType",
        blank=True,
        null=True,
        help_text=_("Note that if you \
            don't select a corporate membership type, \
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
    creator = models.ForeignKey(
        User, related_name="corporate_membership_notice_creator",
        null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(
        User, related_name="corporate_membership_notice_owner",
        null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(choices=STATUS_DETAIL_CHOICES,
                                     default=STATUS_DETAIL_ACTIVE, max_length=50)
    status = models.BooleanField(default=True)

    class Meta:
        app_label = 'corporate_memberships'

    def __unicode__(self):
        return self.notice_name

    def get_default_context(self, corporate_membership=None,
                            recipient=None, **kwargs):
        """
        Returns a dictionary with default context items.
        """
        global_setting = partial(get_setting, 'site', 'global')
        site_url = global_setting('siteurl')

        context = {}

        context.update({
            'site_contact_name': global_setting('sitecontactname'),
            'site_contact_email': global_setting('sitecontactemail'),
            'site_display_name': global_setting('sitedisplayname'),
            'time_submitted': time.strftime("%d-%b-%y %I:%M %p",
                                            datetime.now().timetuple()),
        })

        # return basic context
        if not corporate_membership:
            return context

        # get corp_profile field context
        context.update(corporate_membership.get_field_items())

        if corporate_membership.expiration_dt:
            expire_dt = time.strftime(
                "%d-%b-%y %I:%M %p",
                corporate_membership.expiration_dt.timetuple())
        else:
            expire_dt = ''

        if corporate_membership.payment_method:
            payment_method = corporate_membership.payment_method.human_name
        else:
            payment_method = ''

        if corporate_membership.renewal:
            renewed_individuals_list = \
              render_to_string(
                        'notification/corp_memb_notice_email/renew_list.html',
                        {'corp_membership': corporate_membership})
            total_individuals_renewed = \
                corporate_membership.indivmembershiprenewentry_set.count()
        else:
            renewed_individuals_list = ''
            total_individuals_renewed = ''

        if corporate_membership.invoice:
            invoice_link = '%s%s' % (site_url,
                                     corporate_membership.invoice.get_absolute_url())
        else:
            invoice_link = ''

        corp_app = CorpMembershipApp.objects.current_app()
        authentication_info = render_to_string(
                        'notification/corp_memb_notice_email/auth_info.html',
                        {'corp_membership': corporate_membership,
                         'corp_app': corp_app})

        context.update({
            'expire_dt': expire_dt,
            'payment_method': payment_method,
            'rep_first_name': recipient.user.first_name,
            'renewed_individuals_list': renewed_individuals_list,
            'total_individuals_renewed': total_individuals_renewed,
            'name': corporate_membership.corp_profile.name,
            'email': corporate_membership.corp_profile.email,
            'view_link': "%s%s" % (site_url,
                                   corporate_membership.get_absolute_url()),
            'renew_link': "%s%s" % (site_url,
                                    corporate_membership.get_renewal_url()),
            'invoice_link': invoice_link,
            'individuals_join_url': '%s%s' % (site_url,
                                reverse('membership_default.corp_pre_add',
                                        args=[corporate_membership.id])),
            'authentication_info': authentication_info,
            'anonymous_join_login_info': kwargs.get('anonymous_join_login_info', '')
        })

        return context

    def get_subject(self, corporate_membership=None, recipient=None):
        """
        Return self.subject replace shortcode (context) variables
        The corporate membership object takes priority over entry object
        """
        context = self.get_default_context(corporate_membership, recipient)
        # autoescape off for subject to avoid HTML escaping
        self.subject = '%s%s%s' % (
                        "{% autoescape off %}",
                        self.subject,
                        "{% endautoescape %}")
        return self.build_notice(self.subject, context=context)

    def get_content(self, corporate_membership=None, recipient=None, **kwargs):
        """
        Return self.email_content with footer appended and replace shortcode
        (context) variables
        """
        content = self.email_content + '\n<br /><br />\n{% include "email_footer.html" %}'
        context = self.get_default_context(corporate_membership, recipient, **kwargs)

        return self.build_notice(content, context=context, **kwargs)

    def build_notice(self, content, *args, **kwargs):
        """
        Replace values in a string and return the updated content
        Values are pulled from corporate_membership, and site_settings
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
        within corporate_membership_type specified
        to email addresses specified
        Returns boolean.

        Allowed Notice Types: approve_join, approve_renewal,
        disapprove_join, disapprove_renewal, expiration
        """

        notice_type = kwargs.get('notice_type') or 'joined'
        corp_membership_type = kwargs.get('corporate_membership_type')
        corporate_membership = kwargs.get('corporate_membership')
        recipients = kwargs.get('recipients') or []
        anonymous_join_login_info = kwargs.get('anonymous_join_login_info', '')
        request = kwargs.get('request')

        if not isinstance(corporate_membership, CorpMembership):
            return False

        if isinstance(recipients, basestring):
            recipients = [recipients]  # expecting list of emails

        # allowed notice types
        allowed_notice_types = [
            'approve_join',
            'approve_renewal',
            'disapprove_join',
            'disapprove_renewal',
            'expiration']

        if not notice_type in allowed_notice_types:
            return False

        # recipients list required
        if not recipients:
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
                notice.corporate_membership_type == corp_membership_type,
                notice.corporate_membership_type == None
            )

            if any(notice_requirments):
                for recipient in recipients:
                    extra_context = {
                        'subject': notice.get_subject(
                                    corporate_membership=corporate_membership,
                                    recipient=recipient),
                        'content': notice.get_content(
                                    corporate_membership=corporate_membership,
                                    recipient=recipient,
                                    anonymous_join_login_info=anonymous_join_login_info),
                        'corporate_membership_total': CorpMembership.objects.count(),
                        'sender': notice.sender,
                        'sender_display': notice.sender_display,
                    }
                    if notice.sender:
                        extra_context.update({'reply_to': notice.sender})

                    notification.send_emails(
                        [recipient.user.email],
                        'corp_memb_notice_email', extra_context)
        return True

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())
        super(Notice, self).save(*args, **kwargs)


class NoticeLog(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice = models.ForeignKey(Notice, related_name="logs")
    notice_sent_dt = models.DateTimeField(auto_now_add=True)
    num_sent = models.IntegerField()

    class Meta:
        app_label = 'corporate_memberships'


class NoticeLogRecord(models.Model):
    guid = models.CharField(max_length=50, editable=False)
    notice_log = models.ForeignKey(NoticeLog,
                                   related_name="log_records")
    corp_membership = models.ForeignKey(CorpMembership,
                                   related_name="log_records")
    action_taken = models.BooleanField(default=False)
    action_taken_dt = models.DateTimeField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'corporate_memberships'


def delete_corp_profile(sender, **kwargs):
    corp_membership = kwargs['instance']
    corp_profile = corp_membership.corp_profile

    if not corp_profile.corp_memberships.exists():
        # delete auth domains
        for auth_domain in corp_profile.authorized_domains.all():
            auth_domain.delete()

        # delete reps
        for rep in corp_profile.reps.all():
            rep.delete()
        # delete email verifications
        for email_veri in corp_profile.indivemailverification_set.all():
            email_veri.delete()

        description = 'Corp profile - %s (id=%d) - deleted' % (
                                            corp_profile.name,
                                            corp_profile.id)
        corp_profile.delete()
        EventLog.objects.log(description=description)

post_delete.connect(delete_corp_profile, sender=CorpMembership, weak=False)
