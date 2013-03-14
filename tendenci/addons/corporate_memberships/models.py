import operator
import uuid
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django import forms
from django.utils.importlib import import_module
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.db.models import Q

#from django.contrib.contenttypes.models import ContentType
from tinymce import models as tinymce_models
from tendenci.core.base.utils import day_validate

#from completion import AutocompleteProvider, site
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.apps.invoices.models import Invoice
from tendenci.addons.memberships.models import (MembershipType, App,
                                                MembershipApp,
                                                MembershipDefault,
                                                Membership)
from tendenci.apps.forms_builder.forms.settings import FIELD_MAX_LENGTH, LABEL_MAX_LENGTH
from tendenci.addons.corporate_memberships.managers import (
                                                CorporateMembershipManager,
                                                CorpMembershipManager,
                                                CorpMembershipAppManager)
#from tendenci.core.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import GroupMembership
from tendenci.core.payments.models import PaymentMethod, Payment
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.apps.profiles.models import Profile
from tendenci.core.base.fields import DictField

from tendenci.core.base.utils import send_email_notification
from tendenci.addons.corporate_memberships.settings import use_search_index
from tendenci.addons.corporate_memberships.utils import (
                                            corp_membership_update_perms,
                                            dues_rep_emails_list,
                                            corp_memb_update_perms)
from tendenci.core.imports.utils import get_unique_username
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.addons.industries.models import Industry
from tendenci.addons.regions.models import Region


FIELD_CHOICES = (
                    ("CharField", _("Text")),
                    ("CharField/django.forms.Textarea", _("Paragraph Text")),
                    ("BooleanField", _("Checkbox")),
                    ("ChoiceField", _("Select One from a list (Drop Down)")),
                    ("ChoiceField/django.forms.RadioSelect", _("Select One from a list (Radio Buttons)")),
                    ("MultipleChoiceField", _("Multi select (Drop Down)")),
                    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi select (Checkboxes)")),
                    ("EmailField", _("Email")),
                    ("FileField", _("File upload")),
                    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
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


class CorporateMembershipType(OrderingBaseModel, TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.CharField(_('Description'), max_length=500)
    price = models.DecimalField(_('Price'), max_digits=15, decimal_places=2, blank=True, default=0,
                                help_text="Set 0 for free membership.")
    renewal_price = models.DecimalField(_('Renewal Price'), max_digits=15, decimal_places=2, 
                                        blank=True, default=0, null=True,
                                        help_text="Set 0 for free membership.")
    membership_type = models.ForeignKey(MembershipType, 
                                        help_text=_("Bind individual memberships to this membership type.")) 
    
    admin_only = models.BooleanField(_('Admin Only'), default=0)  # from allowuseroption
    
    apply_threshold = models.BooleanField(_('Allow Threshold'), default=0)
    individual_threshold = models.IntegerField(_('Threshold Limit'), default=0, blank=True, null=True)
    individual_threshold_price = models.DecimalField(_('Threshold Price'), max_digits=15, 
                                                     decimal_places=2, blank=True, null=True, default=0,
                                                     help_text=_("All individual members applying under or " + \
                                                                 "equal to the threashold limit receive the " + \
                                                                 "threshold prices."))
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(CorporateMembershipType, self).save(*args, **kwargs)
      
    # added here temporarily because i cannot use the one in memberships now
    # switch later if the function in memberships is restored.
    def get_expiration_dt(self, renewal=False, join_dt=None, renew_dt=None):
        """
        Calculate the expiration date - for join or renew (renewal=True)
        Examples:
            For join:
                expiration_dt = corporate_membership_type.get_expiration_dt(join_dt=membership.join_dt)
            For renew:
                expiration_dt = corporate_membership_type.get_expiration_dt(renewal=1,
                join_dt=membership.join_dt,
                renew_dt=membership.renew_dt)
        """
        mt = self.membership_type
        now = datetime.now()
        
        if not join_dt or not isinstance(join_dt, datetime):
            join_dt = now
        if renewal and (not renew_dt or not isinstance(renew_dt, datetime)):
            renew_dt = now
        
        if mt.never_expires:
            return None
        
        if mt.period_type == 'rolling':
            if mt.period_unit == 'days':
                return now + timedelta(days=mt.period)
            
            elif mt.period_unit == 'months':
                return now + relativedelta(months=mt.period)
            
            else: # if self.period_unit == 'years':
                if not renewal:
                    if mt.rolling_option == '0':
                        # expires on end of full period
                        return join_dt + relativedelta(years=mt.period)
                    else: # self.expiration_method == '1':
                        # expires on ? days at signup (join) month
                        if not mt.rolling_option1_day:
                            mt.rolling_option1_day = 1
                        expiration_dt = join_dt + relativedelta(years=mt.period)
                        mt.rolling_option1_day = day_validate(datetime(expiration_dt.year, join_dt.month, 1),
                                                                    mt.rolling_option1_day)
                        
                        return datetime(expiration_dt.year, join_dt.month,
                                                 mt.rolling_option1_day, expiration_dt.hour,
                                                 expiration_dt.minute, expiration_dt.second)
                else: # renewal = True
                    if mt.rolling_renew_option == '0':
                        # expires on the end of full period
                        return renew_dt + relativedelta(years=mt.period)
                    elif mt.rolling_renew_option == '1':
                        # expires on the ? days at signup (join) month
                        if not mt.rolling_renew_option1_day:
                            mt.rolling_renew_option1_day = 1
                        expiration_dt = renew_dt + relativedelta(years=mt.period)
                        mt.rolling_renew_option1_day = day_validate(datetime(expiration_dt.year, join_dt.month, 1),
                                                                    mt.rolling_renew_option1_day)
                        return datetime(expiration_dt.year, join_dt.month,
                                                 mt.rolling_renew_option1_day, expiration_dt.hour,
                                                 expiration_dt.minute, expiration_dt.second)
                    else:
                        # expires on the ? days at renewal month
                        if not mt.rolling_renew_option2_day:
                            mt.rolling_renew_option2_day = 1
                        expiration_dt = renew_dt + relativedelta(years=mt.period)
                        mt.rolling_renew_option2_day = day_validate(datetime(expiration_dt.year, renew_dt.month, 1),
                                                                    mt.rolling_renew_option2_day)
                        return datetime(expiration_dt.year, renew_dt.month,
                                                 mt.rolling_renew_option2_day, expiration_dt.hour,
                                                 expiration_dt.minute, expiration_dt.second)
                    
                    
        else: #self.period_type == 'fixed':
            if mt.fixed_option == '0':
                # expired on the fixed day, fixed month, fixed year
                if not mt.fixed_option1_day:
                    mt.fixed_option1_day = 1
                if not mt.fixed_option1_month:
                    mt.fixed_option1_month = 1
                if mt.fixed_option1_month > 12:
                    mt.fixed_option1_month = 12
                if not mt.fixed_option1_year:
                    mt.fixed_option1_year = now.year
                    
                mt.fixed_option1_day = day_validate(datetime(mt.fixed_option1_year,
                                                                  mt.fixed_option2_month, 1),
                                                                    mt.fixed_option2_day)
                    
                return datetime(mt.fixed_option1_year, mt.fixed_option1_month,
                                mt.fixed_option1_day)
            else: # self.fixed_option == '1'
                # expired on the fixed day, fixed month of current year
                if not mt.fixed_option2_day:
                    mt.fixed_option2_day = 1
                if not mt.fixed_option2_month:
                    mt.fixed_option2_month = 1
                if mt.fixed_option2_month > 12:
                    mt.fixed_option2_month = 12
                
                mt.fixed_expiration_day2 = day_validate(datetime(now.year,
                                                                mt.fixed_option2_month, 1),
                                                                mt.fixed_option2_day)
                
                expiration_dt = datetime(now.year, mt.fixed_option2_month,
                                        mt.fixed_option2_day)
                if mt.fixed_option2_can_rollover:
                    if not mt.fixed_option2_rollover_days:
                        mt.fixed_option2_rollover_days = 0
                    if (now - expiration_dt).days <= mt.fixed_option2_rollover_days:
                        expiration_dt = expiration_dt + relativedelta(years=1)
                        
                return expiration_dt


class CorpProfile(TendenciBaseModel):
    guid = models.CharField(max_length=50)
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
    tax_exempt = models.BooleanField(_("Tax exempt"), default=0)

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

    ud1 = models.CharField(max_length=100, blank=True, default='')
    ud2 = models.CharField(max_length=100, blank=True, default='')
    ud3 = models.CharField(max_length=100, blank=True, default='')
    ud4 = models.CharField(max_length=100, blank=True, default='')
    ud5 = models.CharField(max_length=100, blank=True, default='')

    perms = generic.GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")

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


class CorpMembership(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    corp_profile = models.ForeignKey("CorpProfile",
                                     related_name='corp_memberships')
    corporate_membership_type = models.ForeignKey("CorporateMembershipType",
                                    verbose_name=_("MembershipType"))
    renewal = models.BooleanField(default=0)
    renew_dt = models.DateTimeField(_("Renew Date Time"), null=True)
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    join_dt = models.DateTimeField(_("Join Date Time"))
    expiration_dt = models.DateTimeField(_("Expiration Date Time"),
                                         blank=True, null=True)
    approved = models.BooleanField(_("Approved"), default=0)
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

    perms = generic.GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")

    objects = CorpMembershipManager()

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

    def __unicode__(self):
        return "%s" % (self.corp_profile.name)

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid1())
        if not self.entity:
                self.entity_id = 1
        self.allow_anonymous_view = False
        super(CorpMembership, self).save(*args, **kwargs)

    @property
    def module_name(self):
        return self._meta.module_name

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
            if user.profile.is_superuser:
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
                    if use_search_index:
                        filter_or.update({'corp_profile__reps': user})
                    else:
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
                        (value[0], value[1]) for value in corp_members
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

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """
        try:
            from tendenci.apps.notifications import models as notification
        except:
            notification = None
        from tendenci.core.perms.utils import get_notice_recipients

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
                         'approved_denied_user']
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
            payment.method = self.get_payment_method()
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
            corp_memb_type = self.corporate_membership_type
            self.expiration_dt = corp_memb_type.get_expiration_dt(
                                            renewal=True,
                                            join_dt=self.join_dt,
                                            renew_dt=self.renew_dt)
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
                new_membership.expiration_dt = self.expiration_dt
                new_membership.corporate_membership_id = self.id
                new_membership.corp_profile_id = self.corp_profile.id
                new_membership.membership_type = self.corporate_membership_type.membership_type
                new_membership.status = True
                new_membership.status_detail = 'active'
                if not request_user.is_anonymous():
                    new_membership.owner_id = request_user.id
                    new_membership.owner_username = request_user.username

                new_membership.save()
                # archive old memberships
                new_membership.archive_old_memberships()

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
            corp_membership_update_perms(self)

            # TODO:
            # assign object permissions
#            corp_memb_update_perms(self)

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
        # this corporate membership.
        """
        if this_user.is_anonymous():
            return False
        reps = self.corp_profile.reps.all()
        for rep in reps:
            if rep.user.id == this_user.id:
                return True
        return False

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
        t = '<span class="perm-%s">%s</span>'

        if get_setting('module',
                     'corporate_memberships',
                     'anonymoussearchcorporatemembers'):
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
                        status_detail='archive').count()


class CorpMembershipApp(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(_("URL Path"), max_length=155, unique=True)
    corp_memb_type = models.ManyToManyField("CorporateMembershipType",
                                            verbose_name=_("Corp. Memb. Type"))
    authentication_method = models.CharField(_("Authentication Method"),
                                             choices=AUTH_METHOD_CHOICES,
                                    default='admin', max_length=50,
                                    help_text='Define a method for ' + \
                                    'individuals to be bound to their' + \
                                    ' corporate memberships when signing up.')
    description = tinymce_models.HTMLField(_("Description"),
                                    blank=True, null=True,
                                   help_text='Will display at the top of ' + \
                                   'the application form.')
    notes = models.TextField(_("Notes"), blank=True, null=True,
                                   help_text='Notes for editor. ' + \
                                   'Will not display on the application form.')
    confirmation_text = models.TextField(_("Confirmation Text"),
                                         blank=True, null=True)

    memb_app = models.OneToOneField(MembershipApp,
                            help_text=_("App for individual memberships."),
                            related_name='corp_app',
                            verbose_name=_("Membership Application"),
                            null=True)
    payment_methods = models.ManyToManyField(PaymentMethod,
                                             verbose_name="Payment Methods")

    objects = CorpMembershipAppManager()

    class Meta:
        verbose_name = _("Corporate Membership Application")
        verbose_name_plural = _("Corporate Membership Applications")
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("corpmembership_app.preview", [self.id])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(CorpMembershipApp, self).save(*args, **kwargs)


class CorpMembershipAppField(models.Model):
    corp_app = models.ForeignKey("CorpMembershipApp", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    field_name = models.CharField(_("Field Name"), max_length=30, blank=True,
                                  default='')
    field_type = models.CharField(_("Field Type"), choices=FIELD_CHOICES,
                                  max_length=80,
                                  blank=True, null=True,
                                  default='CharField')

    required = models.BooleanField(_("Required"), default=False)
    display = models.BooleanField(_("Show"), default=True)
    admin_only = models.BooleanField(_("Admin Only"), default=False)

    help_text = models.CharField(_("Instruction for User"),
                                 max_length=2000, blank=True, default='')
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
                    null=True,
                    help_text="Comma separated options where applicable")
    # checkbox/radiobutton
    field_layout = models.CharField(_("Choice Field Layout"),
                                    choices=FIELD_LAYOUT_CHOICES,
                                    max_length=50, blank=True,
                                    null=True, default='1')
    size = models.CharField(_("Field Size"), choices=SIZE_CHOICES,
                            max_length=1,
                            blank=True, null=True, default='m')
    default_value = models.CharField(_("Predefined Value"),
                                     max_length=100, blank=True, default='')
    css_class = models.CharField(_("CSS Class Name"),
                                 max_length=50, blank=True, default='')
    order = models.IntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        ordering = ('order',)

    def __unicode__(self):
        if self.field_name:
            return '%s (field name: %s)' % (self.label, self.field_name)
        return '%s' % self.label


class CorpMembershipAuthDomain(models.Model):
    corp_profile = models.ForeignKey("CorpProfile",
                                        related_name="authorized_domains")
    name = models.CharField(max_length=100)


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


class IndivEmailVerification(models.Model):
    guid = models.CharField(max_length=50)
    corp_profile = models.ForeignKey("CorpProfile")
    verified_email = models.CharField(_('email'), max_length=200)
    verified = models.BooleanField(default=0)
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
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    )
    corp_membership = models.ForeignKey("CorpMembership")
    membership = models.ForeignKey(MembershipDefault)
    status_detail = models.CharField(max_length=50,
                                     choices=STATUS_DETAIL_CHOICES,
                                     default='pending')


class CorpMembershipImport(models.Model):
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

    UPLOAD_DIR = "imports/corpmemberships/%s" % uuid.uuid1().get_hex()[:8]

    upload_file = models.FileField(_("Upload File"), max_length=260,
                                   upload_to=UPLOAD_DIR)
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


class CorporateMembership(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(max_length=250, unique=True)
    corporate_membership_type = models.ForeignKey("CorporateMembershipType", verbose_name=_("MembershipType")) 
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, default='', blank=True, null=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zip = models.CharField(_('zipcode'), max_length=50, blank=True, null=True)
    country = models.CharField(_('country'), max_length=50, blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=50, blank=True, null=True)
    email = models.CharField(_('email'), max_length=200,  blank=True, null=True)
    url = models.CharField(_('url'), max_length=100, blank=True, null=True)
    secret_code = models.CharField(max_length=50, blank=True, null=True)
    
    renewal = models.BooleanField(default=0)
    renew_entry_id = models.IntegerField(default=0, blank=True, null=True) 
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField(_("Join Date Time")) 
    renew_dt = models.DateTimeField(_("Renew Date Time"), null=True) 
    expiration_dt = models.DateTimeField(_("Expiration Date Time"), blank=True, null=True)
    approved = models.BooleanField(_("Approved"), default=0)
    approved_denied_dt = models.DateTimeField(_("Approved or Denied Date Time"), null=True)
    approved_denied_user = models.ForeignKey(User, verbose_name=_("Approved or Denied User"), null=True, on_delete=models.SET_NULL)
    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_("Payment Method"), null=True, default=None)
    
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    
    anonymous_creator = models.ForeignKey('Creator', null=True)
    
    corp_app = models.ForeignKey("CorpApp")
    
    perms = generic.GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")
    
    objects = CorporateMembershipManager()
    
    class Meta:
        permissions = (("view_corporatemembership", "Can view corporate membership"),)
        if get_setting('module', 'corporate_memberships', 'label'):
            verbose_name = get_setting('module', 'corporate_memberships', 'label')
            verbose_name_plural = get_setting('module', 'corporate_memberships', 'label_plural')
        else:
            verbose_name = _("Corporate Member")
            verbose_name_plural = _("Corporate Members")
    
    def __unicode__(self):
        return "%s" % (self.name)
    
    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid1())
        super(CorporateMembership, self).save(*args, **kwargs)
        
    @property   
    def module_name(self):
        return self._meta.module_name
    
    @staticmethod
    def get_search_filter(user):
        if user.profile.is_superuser: return None, None
        
        filter_and, filter_or = None, None
        
        allow_anonymous_search = get_setting('module', 
                                     'corporate_memberships', 
                                     'anonymoussearchcorporatemembers')
        allow_member_search = get_setting('module', 
                                  'corporate_memberships', 
                                  'membersearchcorporatemembers')
        
        if allow_anonymous_search or (allow_member_search and user.profile.is_member):
            filter_and =  {'status':1,
                           'status_detail':'active'}
        else:
            if user.is_authenticated():
                filter_or = {'creator': user,
                             'owner': user}
                if use_search_index:
                    filter_or.update({'reps': user})
                else:
                    filter_or.update({'reps__user': user})
            else:
                filter_and = {'allow_anonymous_view':True,}
                
                
        return filter_and, filter_or
        
        
    
    def assign_secret_code(self):
        if not self.secret_code:
            # use the make_random_password in the User object
            length = 6
            allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
            secret_code = User.objects.make_random_password(length=length, allowed_chars=allowed_chars)
            
            # check if this one is unique
            corp_membs = CorporateMembership.objects.filter(secret_code=secret_code)
            
            while corp_membs:
                secret_code = User.objects.make_random_password(length=length, allowed_chars=allowed_chars)
                corp_membs = CorporateMembership.objects.filter(secret_code=secret_code)
                if not corp_membs:
                    break
            self.secret_code = secret_code       
        
    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        """
        return 'Tendenci Invoice %d for Corp. Memb. (%d): %s. ' % (
            inv.id,
            inv.object_id,
            self.name,
        )
        
    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the corporate membership sale
        """
        from tendenci.apps.accountings.models import Acct, AcctEntry, AcctTran
        from tendenci.apps.accountings.utils import make_acct_entries_initial, make_acct_entries_closing
        
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
        
    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """
        from datetime import datetime
        try:
            from tendenci.apps.notifications import models as notification
        except:
            notification = None
        from tendenci.core.perms.utils import get_notice_recipients
         
        # approve it
        if self.renew_entry_id:
            self.approve_renewal(request)
        else:
            self.approve_join(request)
            
        
        # send notification to administrators
        recipients = get_notice_recipients('module', 'corporate_memberships', 'corporatemembershiprecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': self,
                    'request': request,
                }
                notification.send_emails(recipients,'corp_memb_paid', extra_context)

 
    def get_payment_method(self):
        from tendenci.core.payments.models import PaymentMethod
 
        # return payment method if defined
        if self.payment_method:
            return self.payment_method
 
        # first method is credit card (online)
        # will raise exception if payment method does not exist
        self.payment_method = PaymentMethod.objects.get(machine_name='credit-card')
        return self.payment_method
 
    def approve_renewal(self, request, **kwargs):
        """
        Approve the corporate membership renewal, and
        approve the individual memberships that are 
        renewed with the corporate_membership
        """
        from tendenci.addons.corporate_memberships.utils import dues_rep_emails_list
        if self.renew_entry_id:
            renew_entry = CorpMembRenewEntry.objects.get(id=self.renew_entry_id)
            if renew_entry.status_detail not in ['approved', 'disapproved']:
                # 1) archive corporate membership
                self.archive(request.user)
                
                user = request.user
                
                # 2) update the corporate_membership record with the renewal info from renew_entry
                self.renewal = True
                self.corporate_membership_type = renew_entry.corporate_membership_type
                self.payment_method = renew_entry.get_payment_method()
                self.invoice = renew_entry.invoice
                self.renew_dt = renew_entry.create_dt
                self.approved = True
                self.approved_denied_dt = datetime.now()
                if user and (not user.is_anonymous()):
                    self.approved_denied_user = user
                self.status = 1
                self.status_detail = 'active'
                
                corp_memb_type = self.corporate_membership_type
                self.expiration_dt = corp_memb_type.get_expiration_dt(renewal=True,
                                                                join_dt=self.join_dt,
                                                                renew_dt=self.renew_dt)
                self.save()
                
                renew_entry.status_detail = 'approved'
                renew_entry.save()
                
                # 3) approve the individual memberships
                if user and not user.is_anonymous():
                    user_id = user.id
                    username = user.username
                else:
                    user_id = 0
                    username = ''
                group = self.corporate_membership_type.membership_type.group
                
                ind_memb_renew_entries = IndivMembRenewEntry.objects.filter(corp_memb_renew_entry=renew_entry)   
                for memb_entry in ind_memb_renew_entries:
                    membership = memb_entry.membership
                    membership.archive(user)
                    
                    # update the membership record with the renewal info
                    membership.renewal = True
                    membership.renew_dt = self.renew_dt
                    membership.expiration_dt = self.expiration_dt
                    membership.corporate_membership_id = self.id
                    membership.membership_type = self.corporate_membership_type.membership_type
                    membership.status = 1
                    membership.status_detail = 'active'
                    
                    membership.save()

                    # check and add member to the group if not exist
                    try:
                        gm = GroupMembership.objects.get(group=group, member=membership.user)
                    except GroupMembership.DoesNotExist:
                        gm = None
                    if gm:
                        if gm.status_detail != 'active':
                            gm.status_detail = 'active'
                            gm.save()
                    else: 
                        GroupMembership.objects.create(**{
                            'group':group,
                            'member':membership.user,
                            'creator_id': user_id,
                            'creator_username': username,
                            'owner_id':user_id,
                            'owner_username':username,
                            'status':True,
                            'status_detail':'active',
                        })
                # email dues reps that corporate membership has been approved
                recipients = dues_rep_emails_list(self)
                if not recipients and self.creator:
                    recipients = [self.creator.email]
                extra_context = {
                    'object': self,
                    'request': request,
                    'corp_renew_entry': renew_entry,
                    'invoice': renew_entry.invoice,
                }
                send_email_notification('corp_memb_renewal_approved', recipients, extra_context)
                
    def disapprove_renewal(self, request, **kwargs):
        """
        deny the corporate membership renewal
        set the status detail of renew entry to 'disapproved'
        do we need to de-activate the corporate membership?
        """
        if self.renew_entry_id:
            renew_entry = CorpMembRenewEntry.objects.get(id=self.renew_entry_id)
            if renew_entry.status_detail not in ['approved', 'disapproved']:
                renew_entry.status_detail = 'disapproved'
                renew_entry.save()
                
    def approve_join(self, request, **kwargs):
        self.approved = True
        self.approved_denied_dt = datetime.now()
        if not request.user.is_anonymous():
            self.approved_denied_user = request.user
        self.status = 1
        self.status_detail = 'active'
        self.save()
        
        created, username, password = self.handle_anonymous_creator(**kwargs)
             
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
        send_email_notification('corp_memb_join_approved', recipients, extra_context)
    
    def disapprove_join(self, request, **kwargs):
        self.approved = False
        self.approved_denied_dt = datetime.now()
        self.approved_denied_user = request.user
        self.status = 1
        self.status_detail = 'disapproved'
        self.save()
        
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
                
                [my_user] = User.objects.filter(**params).order_by('-is_active')[:1] or [None]
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
            
            # assign object permissions
            corp_memb_update_perms(self)
            
            # update invoice creator/owner
            if self.invoice:
                self.invoice.creator = assign_to_user
                self.invoice.creator_username = assign_to_user.username
                self.invoice.owner = assign_to_user
                self.invoice.owner_username = assign_to_user.username
                self.invoice.save()
            
            return create_new, assign_to_user.username, params.get('password', '')
        
        return False, None, None
                                          
                
    def is_rep(self, this_user):
        """
        Check if this user is one of the representatives of this corporate membership.
        """
        if this_user.is_anonymous(): return False
        reps = self.reps.all()
        for rep in reps:
            if rep.user.id == this_user.id:
                return True
        return False
    
    def allow_view_by(self, this_user):
        if this_user.profile.is_superuser: return True
        
        if get_setting('module', 
                     'corporate_memberships', 
                     'anonymoussearchcorporatemembers'):
            return True
        
        if not this_user.is_anonymous():
            if self.is_rep(this_user): return True
            if self.creator:
                if this_user.id == self.creator.id: return True
            if self.owner:
                if this_user.id == self.owner.id: return True
                
        return False
    
    def allow_edit_by(self, this_user):
        if this_user.profile.is_superuser: return True
        
        if not this_user.is_anonymous():
            if self.status == 1 and (self.status_detail not in ['inactive', 'admin hold'] ):
                if self.is_rep(this_user): return True
                if self.creator:
                    if this_user.id == self.creator.id: return True
                if self.owner:
                    if this_user.id == self.owner.id: return True
                
        return False
    
    @property
    def obj_perms(self):
        t = '<span class="perm-%s">%s</span>'
 
        if get_setting('module', 
                     'corporate_memberships', 
                     'anonymoussearchcorporatemembers'):
            value = t % ('public','Public')
        else:
            value = t % ('private','Private')

        return mark_safe(value)
    
    
    def get_renewal_period_dt(self):
        """
        calculate and return a tuple of renewal period dt:
         (renewal_period_start_dt, renewal_period_end_dt)
        """
        if not self.expiration_dt or not isinstance(self.expiration_dt, datetime):
            return (None, None)
        
        start_dt = self.expiration_dt - timedelta(days=self.corporate_membership_type.membership_type.renewal_period_start)
        end_dt = self.expiration_dt + timedelta(days=self.corporate_membership_type.membership_type.renewal_period_end)
        
        return (start_dt, end_dt)
        
    def can_renew(self):
        if not self.expiration_dt or not isinstance(self.expiration_dt, datetime):
            return False
        
        (renewal_period_start_dt, renewal_period_end_dt) = self.get_renewal_period_dt()
        
        now = datetime.now()
        return (now >= renewal_period_start_dt and now <= renewal_period_end_dt)
    
    def get_pending_renewal_entry(self):
        try:
            return CorpMembRenewEntry.objects.get(id=self.renew_entry_id, 
                                                  status_detail__in=['pending', 'paid - pending approval'])
        except CorpMembRenewEntry.DoesNotExist:
            return None
        
    
    @property
    def is_join_pending(self):
        return self.status_detail in ['pending', 'paid - pending approval']
    
    @property
    def is_renewal_pending(self):
        renew_entry = self.get_pending_renewal_entry()
        return renew_entry <> None
    
    @property
    def is_pending(self):
        return self.is_join_pending or self.is_renewal_pending
        
    
    @property
    def is_expired(self):
        if not self.expiration_dt or not isinstance(self.expiration_dt, datetime):
            return False
        return datetime.now() >= self.expiration_dt
    
    @property
    def is_in_grace_period(self):
        if self.is_expired:
            grace_period_end_dt = self.expiration_dt + timedelta(days=self.corporate_membership_type.membership_type.expiration_grace_period)
            
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
            
    
    def archive(self, user=None):
        """
        Copy self to the CorporateMembershipArchive table
        """
        corp_memb_archive = CorporateMembershipArchive()
        
        field_names = [field.name for field in self.__class__._meta.fields]
        field_names.remove('id')
        
        for name in field_names:
            setattr(corp_memb_archive, name, getattr(self, name))
            
        corp_memb_archive.corporate_membership = self
        corp_memb_archive.corp_memb_create_dt = self.create_dt
        corp_memb_archive.corp_memb_update_dt = self.update_dt
        if user and (not user.is_anonymous()):
            corp_memb_archive.archive_user = user
        corp_memb_archive.save()

    @property
    def entry_items(self):
        """
        Returns a dictionary of entry items from
        the approved entry that is associated with this membership.
        """
        return self.get_entry_items()
        
    
    def get_entry_items(self, slugify_label=True):
        items = {}
        entry = self

        if entry:
            for field in entry.fields.all():
                label = field.field.label
                if slugify_label:
                    label = slugify(label).replace('-','_')
                items[label] = field.value

        return items

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
       
class AuthorizedDomain(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership", related_name="auth_domains")
    name = models.CharField(max_length=100)
        
class CorporateMembershipRep(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership",
                                             related_name="reps")
    user = models.ForeignKey(User, verbose_name=_("Representative"),)
    is_dues_rep = models.BooleanField(_('is dues rep?'), default=0, blank=True)
    is_member_rep = models.BooleanField(_('is member rep?'), default=0, blank=True)
    #is_alternate_rep = models.BooleanField(_('is alternate rep?'), default=0, blank=True)
    
    class Meta:
        unique_together = (("corporate_membership", "user"),)
    
    
class CorporateMembershipArchive(TendenciBaseModel):
    corporate_membership = models.ForeignKey('CorporateMembership')
    guid = models.CharField(max_length=50)
    corporate_membership_type = models.ForeignKey("CorporateMembershipType") 
    name = models.CharField(max_length=250)
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, default='', blank=True, null=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zip = models.CharField(_('zipcode'), max_length=50, blank=True, null=True)
    country = models.CharField(_('country'), max_length=50, blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=50, blank=True)
    email = models.CharField(_('email'), max_length=200,  blank=True)
    url = models.CharField(_('url'), max_length=100, blank=True, null=True)
    #authorized_domains = models.CharField(max_length=500, blank=True, null=True)
    secret_code = models.CharField(max_length=50, blank=True, null=True)
    
    renewal = models.BooleanField(default=0)
    renew_entry_id = models.IntegerField(default=0, blank=True, null=True) 
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField(_("Join Date Time")) 
    renew_dt = models.DateTimeField(_("Renew Date Time"), null=True) 
    expiration_dt = models.DateTimeField(_("Expiration Date Time"), null=True)
    approved = models.BooleanField(_("Approved"), default=0)
    approved_denied_dt = models.DateTimeField(_("Approved or Denied Date Time"), null=True)
    approved_denied_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    #payment_method = models.CharField(_("Payment Method"), max_length=50)
    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_("Payment Method"), null=True, default=None)

    corp_memb_create_dt = models.DateTimeField()
    corp_memb_update_dt = models.DateTimeField()
    
    archive_user = models.ForeignKey(User, related_name="corp_memb_archiver", null=True, on_delete=models.SET_NULL)
    
    
    class Meta:
        verbose_name = _("Corporate Membership Archive")
        verbose_name_plural = _("Corporate Membership Archives")
    
    def __unicode__(self):
        return "ID: %s Archive for %s" % (self.pk, self.corporate_membership)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(CorporateMembershipArchive, self).save(*args, **kwargs)
        
class CorpMembRenewEntry(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership")
    corporate_membership_type = models.ForeignKey("CorporateMembershipType")
    payment_method = models.CharField(_("Payment Method"), max_length=50)
    
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    status_detail = models.CharField(max_length=50)   # pending, approved and disapproved

    @property   
    def module_name(self):
        return self._meta.module_name.lower()
    
    def indiv_memb_renew_entries(self):
        return self.indivmembrenewentry_set.all()
    
    def get_payment_description(self, inv):
        return self.corporate_membership.get_payment_description(inv)
    
    def make_acct_entries(self, user, inv, amount, **kwargs):
        return self.corporate_membership.make_acct_entries(user, inv, amount, **kwargs)
    
    def auto_update_paid_object(self, request, payment):
        return self.corporate_membership.auto_update_paid_object(request, payment)

    def get_payment_method(self):
        from tendenci.core.payments.models import PaymentMethod

        # return payment method if defined
        if self.payment_method and self.payment_method.isdigit():
            return PaymentMethod.objects.get(pk=int(self.payment_method))

        # first method is credit card (online)
        # will raise exception if payment method does not exist
        return PaymentMethod.objects.get(machine_name='credit-card') 

    
class IndivMembRenewEntry(models.Model):
    corp_memb_renew_entry = models.ForeignKey("CorpMembRenewEntry")
    membership = models.ForeignKey(Membership)

    
class IndivMembEmailVeri8n(models.Model):
    guid= models.CharField(max_length=50)
    corporate_membership = models.ForeignKey("CorporateMembership")
    verified_email = models.CharField(_('email'), max_length=200)
    verified = models.BooleanField(default=0)
    verified_dt = models.DateTimeField(null=True)
    creator = models.ForeignKey(User, related_name="ime_veri8n_creator", null=True, on_delete=models.SET_NULL)  
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name="ime_veri8n_updator", null=True, on_delete=models.SET_NULL) 
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(IndivMembEmailVeri8n, self).save(*args, **kwargs)    
    
    
class CorpFieldEntry(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership", related_name="fields")
    field = models.ForeignKey("CorpField", related_name="field")
    value = models.CharField(max_length=FIELD_MAX_LENGTH)
    
    
class CorpApp(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(_("URL Path"), max_length=155, unique=True)
    corp_memb_type = models.ManyToManyField("CorporateMembershipType", verbose_name=_("Corp. Memb. Type"))
    authentication_method = models.CharField(_("Authentication Method"), choices=AUTH_METHOD_CHOICES, 
                                    default='admin', max_length=50, 
                                    help_text='Define a method for individuals to be bound to their corporate memberships when signing up.')
    #description = models.TextField(_("Description"),blank=True, null=True, 
    #                               help_text='Will display at the top of the application form.')
    description = tinymce_models.HTMLField(_("Description"),blank=True, null=True, 
                                   help_text='Will display at the top of the application form.')
    notes = models.TextField(_("Notes"),blank=True, null=True, 
                                   help_text='Notes for editor. Will not display on the application form.')
    confirmation_text = models.TextField(_("Confirmation Text"), blank=True, null=True)
    
    memb_app = models.OneToOneField(App, help_text=_("App for individual memberships."), 
                                    related_name='corp_app', verbose_name=_("Membership Application")) 
    payment_methods = models.ManyToManyField(PaymentMethod, verbose_name="Payment Methods")
   
    #use_captcha = models.BooleanField(_("Use Captcha"), default=1)
    #require_login = models.BooleanField(_("Require User Login"), default=0)
    
    class Meta:
        permissions = (("view_corpapp","Can view corporate membership application"),)
        verbose_name = _("Corporate Membership Application")
        verbose_name_plural = _("Corporate Membership Applications")
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("corp_memb.add", [self.slug])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(CorpApp, self).save(*args, **kwargs)
 
       
class CorpField(OrderingBaseModel):
    corp_app = models.ForeignKey("CorpApp", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    # hidden fields - field_name and object_type
    field_name = models.CharField(_("Field Name"), max_length=30, blank=True, null=True, editable=False)
    #object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_type = models.CharField(_("Map to"), max_length=50, blank=True, null=True)
    field_type = models.CharField(_("Field Type"), choices=FIELD_CHOICES, max_length=80, 
                                  blank=True, null=True, default='CharField')
    
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
                                help_text="Comma separated options where applicable")
    # checkbox/radiobutton
    field_layout = models.CharField(_("Choice Field Layout"), choices=FIELD_LAYOUT_CHOICES, 
                                    max_length=50, blank=True, null=True, default='1')
    size = models.CharField(_("Field Size"), choices=SIZE_CHOICES,  max_length=1,
                            blank=True, null=True, default='m')
                                  
    required = models.BooleanField(_("Required"), default=False)
    no_duplicates = models.BooleanField(_("No Duplicates"), default=False)
    visible = models.BooleanField(_("Visible"), default=True)
    admin_only = models.BooleanField(_("Admin Only"), default=0)   
    
    instruction = models.CharField(_("Instruction for User"), max_length=2000, blank=True, null=True)
    default_value = models.CharField(_("Predefined Value"), max_length=100, blank=True, null=True)
    css_class = models.CharField(_("CSS Class Name"), max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        
    def __unicode__(self):
        if self.field_name:
            return '%s (field name: %s)' % (self.label, self.field_name)
        return '%s' % self.label
    
    def get_field_class(self, initial=None):
        """
            Generate the form field class for this field.
        """
        if self.label and self.id:
            if self.field_type not in ['section_break', 'page_break']:
                if self.field_name in ['corporate_membership_type', 'payment_method']:
                    if not self.field_type:
                        self.field_type = "ChoiceField/django.forms.RadioSelect"
                if "/" in self.field_type:
                    field_class, field_widget = self.field_type.split("/")
                else:
                    field_class, field_widget = self.field_type, None
                field_class = getattr(forms, field_class)
                field_args = {"label": self.label, 
                              "required": self.required,
                              'help_text':self.instruction}
                arg_names = field_class.__init__.im_func.func_code.co_varnames
                if initial:
                    field_args['initial'] = initial
                else:
                    if self.default_value:
                        field_args['initial'] = self.default_value
                if "max_length" in arg_names:
                    field_args["max_length"] = FIELD_MAX_LENGTH
                if "choices" in arg_names:
                    if self.field_name not in ['corporate_membership_type', 'payment_method']:
                        choices = self.choices.split(",")
                        field_args["choices"] = zip(choices, choices)
                if field_widget is not None:
                    module, widget = field_widget.rsplit(".", 1)
                    field_args["widget"] = getattr(import_module(module), widget)
                    
                return field_class(**field_args)
        return None
    
    def get_value(self, corporate_membership, **kwargs):
        if self.field_type not in ['section_break', 'page_break']:
            if self.field_name and self.object_type:
                if self.field_name == 'authorized_domains':
                    return ', '.join([ad.name for ad in corporate_membership.auth_domains.all()])
                if self.field_name == 'expiration_dt' and (not corporate_membership.expiration_dt):
                    return "Never Expire"
                if self.field_name == 'reps':
                    # get representatives
                    return CorporateMembershipRep.objects.filter(
                                    corporate_membership=corporate_membership).order_by('user')
                if self.object_type == 'corporate_membership' and hasattr(corporate_membership, 
                                                                          self.field_name):
                    return getattr(corporate_membership, self.field_name)
            else:
                entry = self.field.filter(corporate_membership=corporate_membership)
                
                if entry:
                    return entry[0].value
        return ''
    
    def get_entry(self, corporate_membership, **kwargs):
        if self.field_type not in ['section_break', 'page_break']:
            if not (self.field_name and self.object_type):
                entry = self.field.filter(corporate_membership=corporate_membership)
                
                if entry:
                    return entry[0]
        return None
