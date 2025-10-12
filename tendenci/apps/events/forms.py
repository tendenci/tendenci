from builtins import str
import re
import imghdr
import calendar
from ast import literal_eval
from os.path import splitext, basename
from datetime import date, datetime, timedelta
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import requests

from django import forms
from django.db.models import Q
from django.forms.widgets import RadioSelect
from django.utils.translation import gettext_lazy as _
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms.utils import ErrorList
from importlib import import_module
from django.contrib.auth.models import User, AnonymousUser
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import messages

# from captcha.fields import CaptchaField
from tendenci.apps.events.models import (
    Event, Place, RegistrationConfiguration, Payment,
    Sponsor, Organizer, Speaker, Type, TypeColorSet,
    RegConfPricing, Addon, AddonOption, CustomRegForm,
    CustomRegField, CustomRegFormEntry, CustomRegFieldEntry,
    RecurringEvent, Registrant, EventCredit, EventStaff,
    AssetsPurchase
)

from tendenci.libs.form_utils.forms import BetterModelForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.payments.models import PaymentMethod
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.fields import EmailVerificationField, CountrySelectField, StateSelectField, PercentField, PriceField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.base.utils import tcurrency
from tendenci.apps.emails.models import Email
from tendenci.apps.files.utils import get_max_file_upload_size
from tendenci.apps.perms.utils import get_query_filters, get_groups_query_filters, has_perm
from tendenci.apps.site_settings.models import Setting
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import Group
from tendenci.apps.discounts.models import Discount
from tendenci.apps.profiles.models import Profile
from tendenci.apps.events.models import ZoomAPIConfiguration
from tendenci.apps.events.settings import FIELD_MAX_LENGTH
from tendenci.apps.base.forms import CustomCatpchaField
from tendenci.apps.base.widgets import PercentWidget
from tendenci.apps.base.forms import ProhibitNullCharactersValidatorMixin
from tendenci.apps.files.validators import FileValidator

from .fields import UseCustomRegField
from .widgets import UseCustomRegWidget
from tendenci.apps.base.http import Http403

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)

EMAIL_AVAILABLE_TOKENS = ['event_title',
                          'event_date',
                          'event_location',
                          'event_link',
                          'qr_code',
                          ]


SEARCH_CATEGORIES_ADMIN = (
    ('title__icontains', _('Event Title')),
    ('description__icontains', _('Event Description')),
    ('id', 'Event ID'),
    ('place__name__icontains', _('Event Location - Name')),
    ('place__address__icontains', _('Event Location - Address')),
    ('place__city__icontains', _('Event Location - City')),
    ('place__county__icontains', _('Event Location - County')),
    ('place__state__icontains', _('Event Location - State')),
    ('tags__icontains', _('Tags')),

    ('priority', _('Priority Events')),

    ('creator__id', _('Creator Userid(#)')),
    ('creator__username', _('Creator Username')),
    ('owner__id', _('Owner Userid(#)')),
    ('owner__username', _('Owner Username')),
)

SEARCH_CATEGORIES = (
    ('title__icontains', _('Event Title')),
    ('description__icontains', _('Event Description')),
    ('id', _('Event ID')),
    ('place__name__icontains', _('Event Location - Name')),
    ('place__address__icontains', _('Event Location - Address')),
    ('place__city__icontains', _('Event Location - City')),
    ('place__county__icontains', _('Event Location - County')),
    ('place__state__icontains', _('Event Location - State')),
    ('tags__icontains', _('Tags')),

    ('priority', _('Priority Events')),
)


def management_forms_tampered(formsets=None):
    """
    Check if management_form is tampered for the list of formsets.
    """
    if formsets:
        for formset in formsets:
            try:
                formset.management_form
            except ValidationError:
                return True
    return False

def get_search_group_choices():
    event_group_ids = set(Event.objects.all().values_list('groups', flat=True))
    groups = Group.objects.filter(
                    show_for_events=True,
                    id__in=event_group_ids).distinct(
                    ).order_by('name').values_list('id', 'label', 'name')
    return [(id, label or name) for id, label, name in groups]

class EventMonthForm(ProhibitNullCharactersValidatorMixin, forms.Form):
    events_in = forms.CharField(label=_('Events In'), required=False,)
    search_text = forms.CharField(label=_('Search'), required=False,)
    group = forms.ChoiceField(required=False, choices=[])
    event_type = forms.ChoiceField(label=_('Type'), required=False, choices=[])
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EventMonthForm, self).__init__(*args, **kwargs)

        group_choices = get_search_group_choices()
        self.fields['group'].choices = [('','All Groups')] + list(group_choices)

        type_choices = Type.objects.all().order_by('name').values_list('slug', 'name')
        self.fields['event_type'].choices = [('','All')] + list(type_choices)

        self.fields['events_in'].widget.attrs.update({'placeholder': 'Date',
                                                      'class': 'form-control input-sm'})
        self.fields['search_text'].widget.attrs.update({'placeholder': 'Keyword',
                                                        'class': 'form-control input-sm'})
        self.fields['group'].widget.attrs.update({'class': 'form-control input-sm'})
        self.fields['event_type'].widget.attrs.update({'class': 'form-control input-sm'})
    

class EventSearchForm(forms.Form):
    start_dt = forms.CharField(label=_('Start Date'), required=False,
                               widget=forms.TextInput(attrs={'class': 'datepicker'}))
    end_dt = forms.CharField(label=_('End Date'), required=False,
                               widget=forms.TextInput(attrs={'class': 'datepicker'}))
    event_type = forms.ChoiceField(label=_('Event Type'), required=False, choices=[])
    event_group = forms.ChoiceField(label=_('Event Group'), required=False, choices=[])
    event_place_type = forms.ChoiceField(label=_('Virtual or In Person'), required=False,
                                         choices=[('', _('All')),
                                                  ('virtual', _('Virtual')),
                                                  ('in_person', _('In person')),])
    national_only = forms.BooleanField(required=False)
    registration = forms.BooleanField(label=_("Events I Have Registered For"), required=False)
    search_category = forms.ChoiceField(choices=SEARCH_CATEGORIES_ADMIN, required=False)
    q = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EventSearchForm, self).__init__(*args, **kwargs)

        if user and not user.is_authenticated:
            del self.fields['registration']
        if user and not user.is_superuser:
            self.fields['search_category'].choices = SEARCH_CATEGORIES
        if not Place.objects.filter(virtual=True).exists():
            # remove the virtual field if there is no virtual events
            del self.fields['event_place_type']
        if not Place.objects.filter(national=True).exists():
            # remove the national field if there is no national events
            del self.fields['national_only']

        type_choices = Type.objects.all().order_by('name').values_list('slug', 'name')
        self.fields['event_type'].choices = [('','All')] + list(type_choices)

        group_choices = get_search_group_choices()
        self.fields['event_group'].choices = [('','All')] + list(group_choices)

        self.fields['start_dt'].initial = datetime.now().strftime('%Y-%m-%d')
        # state
        if get_setting('module', 'events', 'stateusedropdown'):
            self.fields['state'] = StateSelectField(label=_('Select a State'),
                                                    empty_label=_('Select a State'),
                                                    required=False)
        
        for field in self.fields:
            if field not in ['registration', 'national_only']:
                widget_attrs = self.fields[field].widget.attrs 
                if 'class' in widget_attrs:
                    class_attr = widget_attrs['class'] + ' form-control-custom'
                else:
                    class_attr = 'form-control-custom'

                self.fields[field].widget.attrs.update({'class': class_attr})

    def clean(self):
        cleaned_data = super(EventSearchForm, self).clean()
        q = self.cleaned_data.get('q', None)
        cat = self.cleaned_data.get('search_category', None)

        if cat is None or cat == "" :
            if not (q is None or q == ""):
                self._errors['search_category'] =  ErrorList([_('Select a category')])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                int(q)
            except ValueError:
                self._errors['q'] = ErrorList([_('IDs must be an integer')])

        return cleaned_data


class EventSimpleSearchForm(forms.Form):
    search_category = forms.ChoiceField(choices=SEARCH_CATEGORIES_ADMIN, required=False)
    q = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EventSimpleSearchForm, self).__init__(*args, **kwargs)

        if user and not user.is_superuser:
            self.fields['search_category'].choices = SEARCH_CATEGORIES

    def clean(self):
        cleaned_data = super(EventSimpleSearchForm, self).clean()
        q = self.cleaned_data.get('q', None)
        cat = self.cleaned_data.get('search_category', None)

        if cat is None or cat == "" :
            if not (q is None or q == ""):
                self._errors['search_category'] =  ErrorList([_('Select a category')])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                int(q)
            except ValueError:
                self._errors['q'] = ErrorList([_('IDs must be an integer')])

        return cleaned_data


class CustomRegFormAdminForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=(('draft', _('Draft')), ('active', _('Active')), ('inactive', _('Inactive'))))
    #used = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = CustomRegForm
        fields = (
            'name',
            'notes',
            'status',
            'first_name',
            'last_name',
            'mail_name',
            'address',
            'city',
            'state',
            'zip',
            'country',
            'phone',
            'email',
            'position_title',
            'company_name',
            'meal_option',
            'comments',
        )


class CustomRegFormForField(forms.ModelForm):
    class Meta:
        model = CustomRegField
        exclude = ["position"]

    def clean(self):
        cleaned_data = super(CustomRegFormForField, self).clean()
        field_function = cleaned_data.get("field_function")
        field_type = cleaned_data.get("field_type")
        choices = cleaned_data.get("choices")

        if field_function == "GroupSubscription":
            if field_type != "BooleanField":
                raise forms.ValidationError("This field's function requires Checkbox as a field type")
            if not choices:
                raise forms.ValidationError("This field's function requires at least 1 group specified.")
            else:
                for val in choices.split(','):
                    try:
                        Group.objects.get(name=val.strip())
                    except Group.DoesNotExist:
                        raise forms.ValidationError("The group \"%s\" does not exist" % (val))

        return cleaned_data


class AttendanceDatesMixin:
    """Mixin for forms that use pricing attendance dates"""
    def add_attendance_dates(self):
        """Add attendance dates if required by Event"""
        if self.event and self.event.requires_attendance_dates:
            days = self.event.full_event_days if self.user and hasattr(self.user, 'profile') and self.user.profile.is_superuser else self.event.days

            self.fields['attendance_dates'] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                choices = [(date, date) for date in days]
            )

    def clean_attendance_dates(self):
        """Validate attendance_dates field in comparison to days pricing covers"""
        attendance_dates = self.cleaned_data.get('attendance_dates')

        pricing = self.cleaned_data.get('pricing')

        # If we shouldn't be using attenedance dates, return an empty list
        if (
                not self.event or not pricing or not
                pricing.requires_attendance_dates or not
                pricing.available
        ):
            return list()
 
        # Allow people to register for LESS dates covered, but not more
        total_available_days = len(self.event.full_event_days)
        if pricing.days_price_covers > total_available_days:
            pricing.days_price_covers = total_available_days
        if not attendance_dates or len(attendance_dates) > pricing.days_price_covers:
            raise forms.ValidationError(_(f'Please select up to {pricing.days_price_covers} dates.'))

        return attendance_dates


def attendance_dates_callback(field, event, is_admin):
    """Add attendance_dates when using modelformset_factory if applicable"""
    if field.name == 'attendance_dates' and event.requires_attendance_dates:
        days = event.full_event_days if  is_admin else event.days

        return forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                choices = [(date, date) for date in days]
            )
    return field.formfield()


class FormForCustomRegForm(FormControlWidgetMixin, AttendanceDatesMixin, forms.ModelForm):

    class Meta:
        model = CustomRegFormEntry
        exclude = ("form", "entry_time")

    def __init__(self, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model
        instance and its related field model instances.
        """
        self.user = kwargs.pop('user', AnonymousUser)
        self.request = kwargs.pop('request', None)
        self.custom_reg_form = kwargs.pop('custom_reg_form', None)
        self.event = kwargs.pop('event', None)
        self.entry = kwargs.pop('entry', None)
        self.form_index = kwargs.pop('form_index', None)
        self.validate_pricing = kwargs.pop('validate_pricing', True)
        self.form_fields = self.custom_reg_form.fields.filter(visible=True).order_by('position')

        self.pricings = kwargs.pop('pricings', None)
        self.is_table = kwargs.pop('is_table', False)
        self.default_pricing = kwargs.pop('default_pricing', False)
        if self.event and not self.default_pricing:
            self.default_pricing = getattr(self.event, 'default_pricing', None)

        super(FormForCustomRegForm, self).__init__(*args, **kwargs)
        
        max_length_dict = dict([(field.name, field.max_length) for field in Registrant._meta.fields\
                                if hasattr(field, 'max_length')])
        
        for field in self.form_fields:
            if field.map_to_field:
                field_key = field.map_to_field
            else:
                field_key = "field_%s" % field.id
            if "/" in field.field_type:
                field_class, field_widget = field.field_type.split("/")
            else:
                field_class, field_widget = field.field_type, None

            if field.field_type == 'EmailVerificationField':
                field_class = EmailVerificationField
            else:
                field_class = getattr(forms, field_class)
            field_args = {"label": mark_safe(field.label), "required": field.required}
            arg_names = field_class.__init__.__code__.co_varnames
            if "max_length" in arg_names:
                if field.map_to_field and field.map_to_field in max_length_dict:
                    field_args["max_length"] = max_length_dict[field.map_to_field]
                else:
                    field_args["max_length"] = FIELD_MAX_LENGTH
            if "choices" in arg_names:
                choices = field.choices.split(",")
                field_args["choices"] = list(zip(choices, choices))
            if "initial" in arg_names:
                default = field.default.lower()
                if field_class == "BooleanField":
                    if default == "checked" or default == "true" or \
                        default == "on" or default == "1":
                            default = True
                    else:
                        default = False
            field_args["initial"] = field.default
            #if "queryset" in arg_names:
            #    field_args["queryset"] = field.queryset()
            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                # django.forms.extras moved to django.forms.widgets since Django 1.9
                if module == 'django.forms.extras':
                    module = 'django.forms.widgets'
                field_args["widget"] = getattr(import_module(module), widget)
            self.fields[field_key] = field_class(**field_args)

        # add class attr registrant-email to the email field
        if hasattr(self.fields, 'email'):
            self.fields['email'].widget.attrs = {'class': 'registrant-email'}
#        for field in self.form_fields:
#            if field.map_to_field == "email":
#                self.email_key = "field_%s" % field.id
#                self.fields[self.email_key].widget.attrs = {'class': 'registrant-email'}
#                break

        if self.event:
            reg_conf=self.event.registration_configuration
            # make the fields in the subsequent forms as not required
            if not reg_conf.require_guests_info:
                if self.form_index and self.form_index > 0:
                    for key in self.fields:
                        self.fields[key].required = False
            else:
                # this attr is required for form validation
                self.empty_permitted = False

            # add reminder field if event opted to sending reminders to attendees
            if reg_conf.send_reminder:
                self.fields['reminder'] = forms.BooleanField(label=_('Receive event reminders'),
                                                             required=False, initial=True)

        # certification_track field
        if self.event and self.event.course:
            cert_choices = self.event.get_certification_choices()
            if cert_choices:
                self.fields['certification_track'] = forms.ChoiceField(
                                label=_('Certification track'),
                                choices = cert_choices,
                                required=False)

        # --------------------------
        if self.pricings:
            # add the price options field
            self.fields['pricing'] = forms.ModelChoiceField(
                    label=_('Price Options'),
                    queryset=self.pricings,
                    widget=forms.RadioSelect(attrs={'class': 'registrant-pricing'}),
                    initial=self.default_pricing,
                    )
            self.fields['pricing'].label_from_instance = _get_price_labels
            self.fields['pricing'].empty_label = None

        self.add_attendance_dates()

        # member id
        if hasattr(self.event, 'has_member_price') and not \
                    get_setting('module', 'events', 'hide_member_pricing') and \
                    get_setting('module', 'events', 'requiresmemberid') and \
                    self.event.has_member_price:
            self.fields['memberid'] = forms.CharField(label=_('Member ID'), max_length=50, required=False,
                                help_text=_('Please enter a member ID if a member price is selected.'))

        # add override and override_price to allow admin override the price
        if hasattr(self.event, 'is_table') and hasattr(self.event, 'free_event'):
            if self.event and not self.event.is_table and not self.event.free_event:
                if (not self.user.is_anonymous and self.user.profile.is_superuser):
                    self.fields['override'] = forms.BooleanField(label=_("Admin Price Override?"),
                                                                 required=False)
                    self.fields['override_price'] = forms.DecimalField(label=_("Override Price"),
                                                                max_digits=10,
                                                                decimal_places=2,
                                                                required=False)
                    self.fields['override_price'].widget.attrs.update({'size': '8'})

        if self.event:
            if hasattr(self.event, 'is_table') and hasattr(self.event, 'free_event'):
                if not self.event.is_table and reg_conf.allow_free_pass:
                    self.fields['use_free_pass'] = forms.BooleanField(label=_("Use Free Pass"), required=False)

        # initialize internal variables
        self.price = Decimal('0.00')
        self.saved_data = {}
        # -------------------------
        
        self.add_form_control_class()

    def get_user(self, email=None):
        user = None

        if not email:
            email = self.cleaned_data.get('email', '')

        if email:
            [profile] = Profile.objects.filter(user__email__iexact=email,
                                             user__is_active=True,
                                             status=True,
                                             status_detail='active'
                                             ).order_by('-member_number'
                                            )[:1] or [None]
            if profile:
                user = profile.user

        return user or AnonymousUser()

    def clean_pricing(self):
        pricing = self.cleaned_data['pricing']

        # if pricing allows anonymous, let go.
        if pricing.allow_anonymous:
            return pricing

        if self.validate_pricing:
            # The setting anonymousregistration can be set to 'open', 'validated' and 'strict'
            # Both 'validated' and 'strict' require validation.
            if self.event.anony_setting != 'open':

                # check if user is eligiable for this pricing
                email = self.cleaned_data.get('email', u'')
                registrant_user = self.get_user(email)

                if not registrant_user.is_anonymous:

                    if registrant_user.profile.is_superuser:
                        return pricing

                    if pricing.allow_user:
                        return pricing

                    [registrant_profile] = Profile.objects.filter(user=registrant_user)[:1] or [None]

                    if pricing.allow_member and registrant_profile and registrant_profile.is_member:
                        return pricing

                    if pricing.groups.all():
                        for group in pricing.groups.all():
                            if group.is_member(registrant_user):
                                return pricing

                currency_symbol = get_setting("site", "global", "currencysymbol") or '$'
                err_msg = ""
                redirect_to_403 = False
                if not email:
                    err_msg = 'An email address is required for this price %s%s %s. ' % (
                        currency_symbol, pricing.price, pricing.title)
                else:
                    if pricing.allow_user:
                        if User.objects.filter(email__iexact=email, is_active=False).exists():  
                            activation_link = _('<a href="{activate_link}?email={email}&next={next_path}">HERE</a>').format(
                                                    activate_link=reverse('profile.activate_email'),
                                                    email=requests.utils.quote(email),
                                                    next_path=self.request.get_full_path())
                            err_msg = "The email you entered is associated with an inactive account. "
                            inactive_user_err_msg = err_msg + mark_safe(f'''
                                If it is yours, please click {activation_link} and we'll send you an email to activate your account
                                and then you will be returned to here to register this event.''')
                            self.request.user.inactive_user_err_msg = inactive_user_err_msg
                        else:
                            # user doesn't exists in the system
                            err_msg = f'We do not recognize {email} as a site user. Please check your email address or sign up to the site. '
                    else:
                        if pricing.allow_member:
                            err_msg = "We do not recognize %s as a member." % email
                            if len(self.pricings) == 1:
                                redirect_to_403 = True
                                messages.add_message(self.request, messages.ERROR, err_msg)
                        else:
                            if pricing.groups.all():
                                err_msg = "We do not recognize %s as a member of any of the following %s." % (email, ', '.join(pricing.groups.values_list('name', flat=True)))
                        if not err_msg:
                            err_msg = 'Not eligible for the price.%s%s %s.' % (
                                currency_symbol,
                                pricing.price,
                                pricing.title,)
                        if len(self.pricings) > 1:
                            err_msg += ' Please choose another price option.'
                if redirect_to_403:
                    raise Http403
                raise forms.ValidationError(_(err_msg))

        return pricing

    def clean_memberid(self):
        memberid = self.cleaned_data['memberid']
        pricing = self.cleaned_data.get('pricing', None)
        if not pricing:
            return memberid

        price_requires_member = False

        if pricing.allow_member:
            if not (pricing.allow_anonymous and pricing.allow_user):
                price_requires_member = True

        if not self.user.is_superuser:
            if price_requires_member:
                if not memberid:
                    raise forms.ValidationError(_(
                        "We don't detect you as a member. "
                        "Please choose another price option. "))
            else:
                if memberid:
                    raise forms.ValidationError(_(
                        "You have entered a member id but "
                        "have selected an option that does not "
                        "require membership."
                        "Please either choose the member option "
                        "or remove your member id."))

        return memberid

    def clean_override_price(self):
        override = self.cleaned_data['override']
        override_price = self.cleaned_data['override_price']

        if override:
            if override_price is None:
                raise forms.ValidationError(_('Please enter the override price or uncheck the override.'))
            elif  override_price <0:
                raise forms.ValidationError(_('Override price must be a positive number.'))
        return override_price

    def clean_use_free_pass(self):
        from tendenci.apps.corporate_memberships.utils import get_user_corp_membership
        use_free_pass = self.cleaned_data['use_free_pass']
        email = self.cleaned_data.get('email', '')
        memberid = self.cleaned_data.get('memberid', '')
        corp_membership = get_user_corp_membership(
                                        member_number=memberid,
                                        email=email)
        if use_free_pass:
            if not corp_membership:
                raise forms.ValidationError(_('Not a corporate member for free pass'))
            elif not corp_membership.free_pass_avail:
                raise forms.ValidationError(_('Free pass not available for "%s".' % corp_membership.corp_profile.name))
        return use_free_pass

    def save(self, event, **kwargs):
        """
        Create a FormEntry instance and related FieldEntry instances for each
        form field.
        """
        if event:
            if not self.entry:
                entry = super(FormForCustomRegForm, self).save(commit=False)
                entry.form = self.custom_reg_form
                entry.entry_time = datetime.now()
                entry.save()
            else:
                entry = self.entry
            for field in self.form_fields:
                if field.map_to_field:
                    field_key = field.map_to_field
                else:
                    field_key = "field_%s" % field.id
                value = self.cleaned_data.get(field_key, '')
                if isinstance(value,list):
                    value = ','.join(value)
                if not value: value=''

                field_entry = None
                if self.entry:
                    field_entries = self.entry.field_entries.filter(field=field)
                    if field_entries:
                        # field_entry exists, just do update
                        field_entry = field_entries[0]
                        field_entry.value = value
                if not field_entry:
                    #field_entry = CustomRegFieldEntry(field_id=field.id, entry=entry, value=value)
                    field_entry = CustomRegFieldEntry(field=field, entry=entry, value=value)

                field_entry.save()
            return entry
        return


def _get_price_labels(pricing):
    #currency_symbol = get_setting("site", "global", "currencysymbol") or '$'
    if pricing.target_display():
        target_display = ' (%s)' % pricing.target_display()
    else:
        target_display = ''

    end_dt = '<br/>&nbsp;(Ends ' + str(pricing.end_dt.date()) + ')'
    description = '<br/>&nbsp;<span style="font-weight: normal;">' + str(pricing.description) + '</span>'

    return mark_safe('&nbsp;<strong><span data-price="%s">%s %s%s</span>%s</strong>%s' % (
                                      pricing.price,
                                      tcurrency(pricing.price),
                                      pricing.title,
                                      target_display,
                                      end_dt,
                                      description) )


def _get_assets_purchase_price_labels(pricing):
    if pricing.description:
        description = '<br/>&nbsp;' + pricing.description
    else:
        description = ''
    return mark_safe(f'{tcurrency(pricing.price)} {pricing.title}{description}')


class EventCreditForm(forms.Form):
    ceu_category = forms.CharField(widget=forms.Textarea(attrs={'readonly': 'readonly', 'rows': 3}))
    available  = forms.BooleanField(required=False)
    credit_count = forms.DecimalField(required=False)
    alternate_ceu_id = forms.CharField(required=False)
    event_id = forms.IntegerField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'hidden': True}))
    ceu_category_id = forms.IntegerField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'hidden': True}))

    @staticmethod
    def pre_populate_form(event, category, prefix):
        """Pre-populate form based on category and event"""
        initial = {
            'ceu_category': category.name,
            'ceu_category_id': category.pk,
            'event_id': event.pk,
        }


        # If this credit has been configured for this event, add the details as configured.
        credit = event.get_credit_configuration(category)
        if credit:
            initial['credit_count'] = credit.credit_count
            initial['alternate_ceu_id'] = credit.alternate_ceu_id
            initial['available'] = credit.available

        return EventCreditForm(
            prefix=prefix,
            initial=initial)

    def save(self, apply_changes_to, *args, **kwargs):
        event = Event.objects.get(pk=self.cleaned_data.get('event_id'))
        credit_count = self.cleaned_data.get('credit_count')

        # Update if the Event already has this credit configured, or if credit count was set.
        credit = event.get_or_create_credit_configuration(
            self.cleaned_data.get('ceu_category_id'), credit_count)

        if credit:
            try:
                credit.credit_count = credit_count
                credit.alternate_ceu_id = self.cleaned_data.get('alternate_ceu_id')
                credit.available = self.cleaned_data.get('available', False)
                credit.save(apply_changes_to=apply_changes_to, from_event=event)
            except Exception:
                raise ValidationError(f"{credit.ceu_subcategory} not updated, try again.")
            return credit


class StaffForm(FormControlWidgetMixin, BetterModelForm):
    label = _('Staff Member')

    class Meta:
        model = EventStaff

        fields = (
            'name',
            'role',
            'signature_image',
            'use_signature_on_certificate',
            'include_on_certificate',
        )

        fieldsets = [(_('Staff'), {
          'fields': ['name',
                     'role',
                     'signature_image',
                     'use_signature_on_certificate',
                     'include_on_certificate',
                    ],
          'legend': '',
          'classes': ['boxy-grey'],
          })
        ]


class EventForm(TendenciBaseForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Event._meta.app_label,
        'storme_model':Event._meta.model_name.lower()}))

    start_dt = forms.SplitDateTimeField(label=_('Start Date/Time'),
                                  initial=datetime.now()+timedelta(days=30),
                                  input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
                                  input_time_formats=['%I:%M %p', '%H:%M:%S'])
    end_dt = forms.SplitDateTimeField(label=_('End Date/Time'),
                                initial=datetime.now()+timedelta(days=30, hours=2),
                                input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
                                input_time_formats=['%I:%M %p', '%H:%M:%S'])
    all_day = forms.BooleanField(label=_('All Day'), required=False, initial=False)
    start_event_date = forms.DateField(
        label=_('Start Date'),
        initial=datetime.now().date()+timedelta(days=30),
        widget=forms.DateInput(attrs={'class':'datepicker'}))
    end_event_date = forms.DateField(
        label=_('End Date'),
        initial=datetime.now().date()+timedelta(days=30),
        widget=forms.DateInput(attrs={'class':'datepicker'}))

    photo_upload = forms.FileField(label=_('Photo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current photo'), required=False)
    groups = forms.ModelMultipleChoiceField(required=True, queryset=None, help_text=_('Hold down "Control", or "Command" on a Mac, to select more than one.'))
    primary_group = forms.ModelChoiceField(required=False, queryset=None)

    FREQUENCY_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
    )
    is_recurring_event = forms.BooleanField(label=_('Is Recurring?'), required=False)
    repeat_type = forms.ChoiceField(label=_('Repeats'), choices=RecurringEvent.RECURRENCE_CHOICES, initial=RecurringEvent.RECUR_DAILY)
    frequency = forms.ChoiceField(label=_('Repeats Every'), choices=FREQUENCY_CHOICES, initial=1)
    end_recurring = forms.DateField(
        label=_('Recurring Ends On'), initial=date.today()+timedelta(days=30),
        widget=forms.DateInput(attrs={'class':'datepicker'}))
    recurs_on = forms.ChoiceField(label=_('Recurs On'), widget=forms.RadioSelect, initial='weekday',
        choices=(('weekday', _('the same day of the week')),('date',_('the same date')),))

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),
                 ('inactive',_('Inactive')),
                 ('pending',_('Pending')),
                 ('template',_('Template')),))

    parent = forms.ModelChoiceField(
        required=False,
        queryset=Event.objects.available_parent_events(),
        help_text=_("Larger symposium this event is a part of"),
    )

    repeat_of = forms.ModelChoiceField(
        required=False,
        queryset=Event.objects.none(),
        help_text=_("Select child event this is a repeat of"),
    )

    class Meta:
        model = Event
        fields = (
            'title',
            'course',
            'short_name',
            'event_code',
            'delivery_method',
            'description',
            'event_relationship',
            'parent',
            'repeat_of',
            'start_dt',
            'end_dt',
            'is_recurring_event',
            'repeat_type',
            'frequency',
            'end_recurring',
            'all_day',
            'start_event_date',
            'end_event_date',
            'on_weekend',
            'timezone',
            'priority',
            'type',
            'groups',
            'primary_group',
            'external_url',
            'photo_upload',
            'certificate_image',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'enable_private_slug',
            'private_slug',
            'status_detail',
            )
        widgets = {
            'private_slug': forms.HiddenInput()
        }

        fieldsets = [(_('Event Information'), {
                      'fields': ['title',
                                 'event_relationship',
                                 'parent',
                                 'repeat_of',
                                 'course',
                                 'short_name',
                                 'event_code',
                                 'description',
                                 'is_recurring_event',
                                 'frequency',
                                 'repeat_type',
                                 'all_day',
                                 'start_dt',
                                 'end_dt',
                                 'start_event_date',
                                 'end_event_date',
                                 'recurs_on',
                                 'end_recurring',
                                 ],
                      'legend': ''
                      }),
                      (_('Event Information'), {
                       'fields': ['on_weekend',
                                  'timezone',
                                  'priority',
                                  'delivery_method',
                                  'type',
                                  'groups',
                                  'primary_group',
                                  'external_url',
                                  'photo_upload',
                                  'certificate_image',
                                  'tags',
                                 ],
                      'legend': ''
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 'enable_private_slug',
                                 'private_slug',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })
                    ]

    def __init__(self, *args, **kwargs):
        self.edit_mode = kwargs.pop('edit_mode', False)
        self.recurring_mode = kwargs.pop('recurring_mode', False)
        is_template = kwargs.pop('is_template', False)
        parent_event_id = kwargs.pop('parent_event_id', None)
        super(EventForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(
                pk=self.instance.pk
            )
            # Queryset `available_parent_events` filters out past events so you can't
            # assign a past event to a new child event. However, if this is an old child
            # event, we need to make sure it's an option in the drop down. Since we don't
            # allow changing the parent event once it's set, it is ok for it to be the
            # only option.
            if self.instance.parent:
                self.fields['parent'].queryset = Event.objects.filter(pk=self.instance.parent.pk)

            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            if 'private_slug' in self.fields:
                self.fields['enable_private_slug'].help_text = self.instance.get_private_slug(absolute_url=True)
            self.fields['start_event_date'].initial = self.instance.start_dt.date()
            self.fields['end_event_date'].initial = self.instance.end_dt.date()
        else:
            # kwargs['instance'] always trumps initial
            if 'private_slug' in self.fields:
                self.fields['private_slug'].initial = self.instance.get_private_slug()
                self.fields['enable_private_slug'].widget = forms.HiddenInput()

            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
            #self.fields['groups'].initial = Group.objects.get_or_create_default()
            
        if 'repeat_of' in self.fields:
            if self.instance.pk and self.instance.parent and self.instance.repeat_of: # on event edit, repeat_of already set
                self.fields['repeat_of'].queryset = Event.objects.filter(pk=self.instance.repeat_of.pk)
            elif (self.instance.pk and self.instance.parent) or ('parent' in self.fields and parent_event_id): # on editing sub-event with no repeat, or adding new sub-event
                # Populate repeat_of options with all child events that are not already repeats.
                parent_event = self.instance.parent if self.instance.pk else None
                if not parent_event:
                    parent_event = Event.objects.get(id=parent_event_id)
                queryset = parent_event.child_events.filter(repeat_of__isnull=True)

                # If there's an instance, make sure it's not in the repeat_of options (don't want an Event to repeat itself)
                if self.instance.pk:
                    queryset = queryset.exclude(pk=self.instance.pk)
                self.fields['repeat_of'].queryset = queryset


        if self.instance.image:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.image.pk, basename(self.instance.image.file.name))
        else:
            self.fields.pop('remove_photo')
        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        if self.instance.is_recurring_event:
            message = _('Changes here would be ignored if applied to other events in series.')
            self.fields['start_dt'].help_text = message
            self.fields['end_dt'].help_text = message

        if self.edit_mode:
            self.fields.pop('is_recurring_event')
            self.fields.pop('repeat_type')
            self.fields.pop('frequency')
            self.fields.pop('end_recurring')
            self.fields.pop('recurs_on')
            #self.fields['repeat_of'].widget.attrs.update({'disabled': True})
        else:
            if is_template:
                # hide recurring event fields when adding a template
                self.fields['is_recurring_event'].widget = forms.HiddenInput()
                self.fields['is_recurring_event'].initial = False
                self.fields['repeat_type'].widget = forms.HiddenInput()
                self.fields['frequency'].widget = forms.HiddenInput()
                self.fields['end_recurring'].widget = forms.HiddenInput()
                self.fields['recurs_on'].widget = forms.HiddenInput()

        if self.edit_mode and self.recurring_mode:
            self.fields.pop('start_dt')
            self.fields.pop('end_dt')
            self.fields.pop('start_event_date')
            self.fields.pop('end_event_date')
            self.fields.pop('photo_upload')

        # Set event relationship field to read only if this is a parent
        # event that already has children, or a child event with a parent
        # set
        nested_events = get_setting('module', 'events', 'nested_events')
        if self.edit_mode and nested_events:
            has_child_events = self.instance.pk and self.instance.has_child_events
            if has_child_events or self.instance.parent:
                self.fields['event_relationship'].widget.attrs.update({'disabled': True})

            if self.instance.parent:
                self.fields['parent'].widget.attrs.update({'disabled': True})

        default_groups = Group.objects.filter(status=True, status_detail="active",
                                              show_for_events=True)
        if not self.user.is_superuser:
            # only superuser can change the priority bit
            if 'priority' in self.fields:
                self.fields.pop('priority')

            if get_setting('module', 'user_groups', 'permrequiredingd') == 'change':
                filters = get_groups_query_filters(self.user,)
            else:
                if not has_perm(self.user, 'user_groups.view_group'):
                    filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
                else:
                    # this user has the 'user_groups.view_group' perm
                    filters = None
            if filters:
                default_groups = default_groups.filter(filters).distinct()

        #groups_list = [(0, '---------')] + list(groups_list)
        #self.fields['groups'].choices = groups_list
        self.fields['groups'].queryset = default_groups
        self.fields['timezone'].initial = settings.TIME_ZONE

        if get_setting('module', 'events', 'allowmultigroups'):
            self.fields['primary_group'].queryset = self.fields['groups'].queryset
            self.fields['primary_group'].empty_label = None
            if self.instance and self.instance.pk:
                self.fields['primary_group'].initial = self.instance.primary_group
            self.fields['primary_group'].help_text = _("Primary group's entity will be associated with the invoices created from event registration. ")
            # if self.instance.pk:
            #     primary_group = self.instance.primary_group
            #     if primary_group:
            #         self.fields['primary_group'].queryset = self.fields['groups'].queryset.filter(id=primary_group.id)
                    
        else:
            del self.fields['primary_group']
        
        self.fields['type'].required = True

        # check if course field is needed
        if not get_setting('module', 'events', 'usewithtrainings'):
            if 'course' in self.fields:
                del self.fields['course']
        else:
            if 'course' in self.fields:
                self.fields['course'].queryset = self.fields['course'].queryset.filter(
                    location_type='onsite',
                    status_detail='enabled').order_by('name') # onsite courses only
        
        # If nested events is not enabled, remove it from the form
        if not nested_events:
            if 'event_relationship' in self.fields:
                del self.fields['event_relationship']
            if 'parent' in self.fields:
                del self.fields['parent']
            if 'repeat_of' in self.fields:
                del self.fields['repeat_of']

    def clean_photo_upload(self):
        photo_upload = self.cleaned_data['photo_upload']
        if photo_upload:
            extension = splitext(photo_upload.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError(_('The photo must be of jpg, gif, or png image type.'))

            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError(_('The photo is an invalid image. Try uploading another photo.'))

            max_upload_size = get_max_file_upload_size()
            if photo_upload.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %(max_upload_size)s. Current filesize %(upload_size)s') % {
                                'max_upload_size': filesizeformat(max_upload_size),
                                'upload_size': filesizeformat(photo_upload.size)})

        return photo_upload


    def clean_end_recurring(self):
        end_recurring = self.cleaned_data.get('end_recurring', None)
        if end_recurring:
            return datetime.combine(end_recurring, datetime.max.time())
        return end_recurring

    def clean(self):
        if self.edit_mode and self.recurring_mode:
            # those 4 fields - start_dt, end_dt, start_event_date, and end_event_date - are excluded on recurring events
            return super(EventForm, self).clean()
        else:
            cleaned_data = super(EventForm, self).clean()
            start_dt = cleaned_data.get("start_dt")
            end_dt = cleaned_data.get("end_dt")
            start_event_date = cleaned_data.get('start_event_date')
            end_event_date = cleaned_data.get('end_event_date')

            if not isinstance(start_dt, datetime):
                raise forms.ValidationError(_('Please enter a valid Start Date/Time.'))
            if not isinstance(end_dt, datetime):
                raise forms.ValidationError(_('Please enter a valid End Date/Time.'))

            if start_dt > end_dt:
                errors = self._errors.setdefault("end_dt", ErrorList())
                errors.append(_(u"This cannot be \
                    earlier than the start date."))

            parent = cleaned_data.get("parent")
            if parent and (start_dt < parent.start_dt or end_dt > parent.end_dt):
                if start_dt < parent.start_dt:
                    errors = self._errors.setdefault("start_dt", ErrorList())
                if end_dt > parent.end_dt:
                    errors = self._errors.setdefault("end_dt", ErrorList())
                errors.append(_(f"Sub-events must happen during parent event - {parent}"))

            if start_event_date and end_event_date:
                if start_event_date > end_event_date:
                    errors = self._errors.setdefault("end_event_date", ErrorList())
                    errors.append(_(u"This cannot be \
                        earlier than the start date."))

            # Always return the full collection of cleaned data.
            return cleaned_data

    def save(self, *args, **kwargs):
        event = super(EventForm, self).save(*args, **kwargs)

        # Reset time if All Day is selected
        if event.all_day:
            if self.cleaned_data.get('start_event_date'):
                event.start_dt = datetime.combine(self.cleaned_data.get('start_event_date'), datetime.min.time())
            else:
                event.start_dt = datetime.combine(event.start_dt, datetime.min.time())
            if self.cleaned_data.get('end_event_date'):
                event.end_dt = datetime.combine(self.cleaned_data.get('end_event_date'), datetime.max.time())
            else:
                event.end_dt = datetime.combine(event.end_dt, datetime.max.time())

        if self.cleaned_data.get('remove_photo'):
            event.image = None

        primary_group = self.cleaned_data.get('primary_group', None)
        if primary_group:
            event.primary_group_selected = primary_group

        return event


class DisplayAttendeesForm(forms.Form):
    display_event_registrants = forms.BooleanField(required=False)
    DISPLAY_REGISTRANTS_TO_CHOICES=(("public",_("Everyone")),
                                    ("user",_("Users Only")),
                                    ("member",_("Members Only")),
                                    ("admin",_("Admin Only")),)
    display_registrants_to = forms.ChoiceField(choices=DISPLAY_REGISTRANTS_TO_CHOICES,
                                                widget=forms.RadioSelect,
                                                initial='public')
    label = 'Display Attendees'


class ApplyRecurringChangesForm(forms.Form):
    APPLY_CHANGES_CHOICES = (("self",_("This event only")),
                             ("rest",_("This and the following events in series")),
                             ("all",_("All events in series")))
    apply_changes_to = forms.ChoiceField(choices=APPLY_CHANGES_CHOICES,
                                         widget=forms.RadioSelect, initial="self")


class TypeChoiceField(forms.ModelChoiceField):

    def __init__(self, queryset, empty_label=u"---------",
                 required=True, widget=None, label=None, initial=None, choices=None,
                 help_text=None, to_field_name=None, *args, **kwargs):

        if required and (initial is not None):
            self.empty_label = None
        else:
            self.empty_label = empty_label

        self._choices = ()
        if choices:
            self._choices = choices

        forms.fields.ChoiceField.__init__(self, choices=self._choices, widget=widget)

        self.queryset = queryset
        self.to_field_name = to_field_name


class TypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TypeForm, self).__init__(*args, **kwargs)

        colorsets = TypeColorSet.objects.all()

        color_set_choices = [(color_set.pk,
            mark_safe('<img style="width:25px; height:25px" src="/event-logs/colored-image/%s/" />'
            % color_set.bg_color)) for color_set in colorsets]

        self.fields['color_set'] = TypeChoiceField(
            choices=color_set_choices,
            queryset=colorsets,
            widget=forms.RadioSelect()
        )

    class Meta:
        model = Type
        # django 1.8 requires fields or exclude
        exclude = ()

class ReassignTypeForm(forms.Form):
    type = forms.ModelChoiceField(empty_label=None, initial=1, queryset=Type.objects.none(), label=_('Reassign To'))

    def __init__(self, *args, **kwargs):
        type_id = kwargs.pop('type_id')
        super(ReassignTypeForm, self).__init__(*args, **kwargs)

        event_types = Type.objects.exclude(pk=type_id)

        self.fields['type'].queryset = event_types


class PlaceForm(FormControlWidgetMixin, forms.ModelForm):
    place = forms.ChoiceField(label=_('Place'), required=False, choices=[])
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': Place._meta.app_label,
        'storme_model': Place._meta.model_name.lower()}))
    country = CountrySelectField(label=_('Country'), required=False)
    label = _('Location Information')

    field_order = [
                'virtual',
                'use_zoom_integration',
                'zoom_api_configuration',
                'zoom_meeting_id',
                'zoom_meeting_passcode',
                'is_zoom_webinar',
                'place',
                'name',
                'description',
                'address',
                'city',
                'state',
                'zip',
                'county',
                'country',
                'national',
                'url',
            ]

    class Meta:
        model = Place
        # django 1.8 requires fields or exclude
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        # Populate place
        places = Place.objects.all().order_by(
            'name', 'address', 'city', 'state', 'zip', 'country', '-pk').distinct(
            'name', 'address', 'city', 'state', 'zip', 'country')

        choices = [('', '------------------------------')]
        for p in places:
            choices.append((p.pk, str(p)))
        if self.fields.get('place'):
            self.fields.get('place').choices = choices

        if self.instance.id:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
        if get_setting('module', 'events', 'stateusedropdown'):
            self.fields['state'] = StateSelectField(label=_('State'), required=False)
            self.add_form_control_class()

        default_zoom_config = ZoomAPIConfiguration.objects.filter(use_as_default=True).first()
        if default_zoom_config:
            self.fields['zoom_api_configuration'].initial = default_zoom_config

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        place = super(PlaceForm, self).save(commit=False)
        # Handle case if place is given
        if self.cleaned_data.get('place'):
            place_obj = Place.objects.get(pk=self.cleaned_data.get('place'))
            # Check if there is a change in value.
            # If there is a change in value, create new place
            if place_obj.name != place.name or \
                place_obj.description != place.description or \
                place_obj.address != place.address or \
                place_obj.city != place.city or \
                place_obj.zip != place.zip or \
                place_obj.country != place.country or \
                place_obj.url != place.url:
                place.pk = None
                if commit:
                    place.save()
            else:
                place = place_obj
        else:
            if commit:
                place.save()
        return place


class SpeakerBaseFormSet(BaseModelFormSet):
    def clean(self):
        """Checks that no two speakers have the same name."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        names = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if 'name' in form.cleaned_data:
                name = form.cleaned_data['name']
                if name and name in names:
                    raise forms.ValidationError(_("Speakers in an event must have distinct names. '%s' is already used." % name))
                names.append(name)


class SpeakerForm(FormControlWidgetMixin, BetterModelForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Speaker._meta.app_label,
        'storme_model':Speaker._meta.model_name.lower()}))
    label = _('Speaker')
    file = forms.FileField(required=False)

    class Meta:
        model = Speaker

        fields = (
            'name',
            'file',
            'featured',
            'description',
            'position'
        )

        fieldsets = [(_('Speaker'), {
          'fields': ['name',
                    'file',
                    'featured',
                    'description',
                    'position'
                    ],
          'legend': '',
          'classes': ['boxy-grey'],
          })
        ]

    def __init__(self, *args, **kwargs):
        kwargs.update({'use_required_attribute': False})
        super(SpeakerForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

    def clean_file(self):
        data = self.cleaned_data['file']
        if data:
            max_upload_size = get_max_file_upload_size()
            if data.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %(max_upload_size)s. Current filesize %(data_size)s') % {
                                                    'max_upload_size': filesizeformat(max_upload_size),
                                                    'data_size': filesizeformat(data.size)})

        return data

    def clean(self):
        name = self.cleaned_data['name']
        data = self.cleaned_data['file'] if 'file' in self.cleaned_data else None
        description = self.cleaned_data['description']

        if data and not name:
            raise forms.ValidationError(_('Speaker name is required if a speaker file is given.'))

        if self.instance.pk:
            if not (name or description):
                raise forms.ValidationError(_('Speaker details missing. Please add speaker name or delete the speaker.'))

        return self.cleaned_data


class ImageUploadFormMixin:
    """Mixin to upload an image"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.image:
            name = f"{self.label.lower()}-remove_photo"
            self.fields['image_upload'].help_text = f'<input name="{name}" id="id_{name}" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.image.pk, basename(self.instance.image.file.name))
        self.fields['image_upload'].validators = [FileValidator(allowed_extensions=ALLOWED_LOGO_EXT)]

    def save(self, *args, **kwargs):
        """Remove image if needed"""
        instance = super().save(*args, **kwargs)
        if self.data.get(f'{self.label.lower()}-remove_photo'):
            if instance.image:
                instance.image.delete()
        return instance


class OrganizerForm(ImageUploadFormMixin, FormControlWidgetMixin, forms.ModelForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Organizer._meta.app_label,
        'storme_model':Organizer._meta.model_name.lower()}))
    label = 'Organizer'
    image_upload = forms.FileField(label=_('Logo'), required=False)

    class Meta:
        model = Organizer

        fields = (
            'name',
            'description',
            'image_upload',
        )

    def __init__(self, *args, **kwargs):
        super(OrganizerForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0


class SponsorForm(ImageUploadFormMixin, FormControlWidgetMixin, forms.ModelForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Sponsor._meta.app_label,
        'storme_model':Sponsor._meta.model_name.lower()}))
    label = 'Sponsor'
    image_upload = forms.FileField(label=_('Logo'), required=False)

    class Meta:
        model = Sponsor

        fields = (
            'name',
            'description',
            'image_upload'
        )

    def __init__(self, *args, **kwargs):
        super(SponsorForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        # django 1.8 requires fields or exclude
        exclude = ()


class Reg8nConfPricingForm(FormControlWidgetMixin, BetterModelForm):
    label = "Pricing"
    start_dt = forms.SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now(), help_text=_('The date time this price starts to be available for registration'))
    end_dt = forms.SplitDateTimeField(label=_('End Date/Time'), initial=datetime.now()+timedelta(days=30,hours=6), help_text=_('The date time this price ceases to be available for registration'))
    price = PriceField(label=_('Price'), max_digits=21, decimal_places=2, initial=0.00)
    #dates = Reg8nDtField(label=_("Start and End"), required=False)
    groups = forms.ModelMultipleChoiceField(required=False, queryset=None, help_text=_('Hold down "Control", or "Command" on a Mac, to select more than one. If you have selected one but want to leave groups unselected, hold down "Control" +Z, or "Command" +Z on Mac, then click on the selected group.'))
    payment_required = forms.ChoiceField(required=False,
                                         choices=(('True', _('Yes')), ('False', _('No'))),
                                         initial='True')
    days_price_covers = forms.IntegerField(
        required=False, help_text=_('Number of days this price covers (Optional).'))

    def __init__(self, *args, **kwargs):
        kwargs.pop('reg_form_queryset', None)
        self.user = kwargs.pop('user', None)
        self.reg_form_required = kwargs.pop('reg_form_required', False)
        kwargs.update({'use_required_attribute': False})
        super(Reg8nConfPricingForm, self).__init__(*args, **kwargs)
        kwargs.update({'initial': {'start_dt':datetime.now(),
                        'end_dt': (datetime(datetime.now().year, datetime.now().month, datetime.now().day, 17, 0, 0)
                        + timedelta(days=29))}})
        #self.fields['dates'].build_widget_reg8n_dict(*args, **kwargs)
        self.fields['allow_anonymous'].initial = True

        default_groups = Group.objects.filter(status=True, status_detail="active")

        if not self.user or not self.user.profile.is_superuser:
            filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
            default_groups = default_groups.filter(filters).distinct()

        if not get_setting("module", "events", "nested_events"):
            self.fields['days_price_covers'].widget = forms.HiddenInput()

        self.fields['groups'].queryset = default_groups
        
        # tax rate
        if get_setting('module', 'invoices', 'taxrateuseregions'):
            if self.user and self.user.is_superuser:
                self.fields['tax_rate'].help_text += "<br />Note that this rate will be served as the default rate. Please go to <a href='/admin/regions/region/'>Regions</a> to configure more tax rates."

    def clean_tax_rate(self):
        tax_rate = self.cleaned_data['tax_rate']
        if tax_rate is None:
            tax_rate = 0
        return tax_rate

    def clean_quantity(self):
        # make sure that quantity is always a positive number
        quantity = self.cleaned_data['quantity']
        if quantity is None or quantity <= 0:
            quantity = 1
        return quantity

    def clean(self):
        data = self.cleaned_data
        if 'start_dt' in data and 'end_dt' in data and data['start_dt'] > data['end_dt']:
            raise forms.ValidationError(_('Pricing: Start Date/Time should come before End Date/Time'))
        return data

    class Meta:
        model = RegConfPricing

        fields = [
            'title',
            'position',
            'description',
            'quantity',
            'registration_cap',
            'payment_required',
            'price',
            'assets_purchase',
            'days_price_covers',
            'include_tax',
            'tax_rate',
            'start_dt',
            'end_dt',
            'groups',
            'allow_anonymous',
            'allow_user',
            'allow_member',
            
         ]

        fieldsets = [(_('Registration Pricing'), {
          'fields': ['title',
                     'position',
                    'description',
                    'quantity',
                    'registration_cap',
                    'payment_required',
                    'price',
                    'assets_purchase',
                    'days_price_covers',
                    'include_tax',
                    'tax_rate',
                    'start_dt',
                    'end_dt',
                    #'dates',
                    'groups',
                    'allow_anonymous',
                    'allow_user',
                    'allow_member',
                   
                    ],
          'legend': '',
          'classes': ['boxy-grey'],
          'description': _('Note: the registrants will be verified (for users, ' + \
                        'members or a specific group) if and only if the setting' + \
                        ' <strong>Anonymous Event Registration</strong> is ' + \
                        'set to "validated" or "strict".' + \
                        ' <a href="/settings/module/events/anonymousregistration" ' + \
                        'target="_blank">View or update the setting</a>. ')
                         #  Note that: cannot use reverse setting url here...
          })             #  it would break everything.
        ]

    def save(self, *args, **kwargs):
        """
        Save a pricing and handle the reg_form
        """
        if not self.reg_form_required:
            self.cleaned_data['reg_form'] = None
        else:
            # To clone or not to clone? -
            # clone the custom registration form only if it's a template.
            # in other words, it's not associated with any pricing or regconf
            reg_form = self.cleaned_data['reg_form']
            if reg_form.is_template:
                self.cleaned_data['reg_form'] = reg_form.clone()

        return super(Reg8nConfPricingForm, self).save(*args, **kwargs)


class Reg8nEditForm(FormControlWidgetMixin, BetterModelForm):
    label = _('Registration')
    limit = forms.IntegerField(
            label=_('Registration Limit'),
            initial=0,
            help_text=_("Enter the maximum number of registrants. Use 0 for unlimited registrants")
    )
    payment_method = forms.ModelMultipleChoiceField(
        queryset=PaymentMethod.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=[1,2,3]) # first three items (inserted via fixture)
    use_custom_reg = UseCustomRegField(label="Custom Registration Form", required=False)

    registration_email_text = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':RegistrationConfiguration._meta.app_label,
        'storme_model':RegistrationConfiguration._meta.model_name.lower()}))

    cancellation_fee = PriceField(
        label=_('Cancellation Fee'),
        max_digits=21,
        decimal_places=2,
        initial=0.00,
        help_text=_('Fee registrant pays when cancelling. ' \
                    'Leave as 0 if there is no cancellation fee. ' \
                    'If cancellation percent is set, that will be used instead.'
                    )
    )

    cancellation_percent = PercentField(
        label=_('Cancellation Percent'),
        allowed_decimal_places=0,
        help_text=_(
            'Percent of total price registrant pays when cancelling. ' \
            'If percent is set, this is used to calculate cancellation fee, ' \
            'overriding other configuration for cancellation fee. ' \
            'Leave as 0% to set cancellation fee directly instead.'
        )
    )

    cancel_by_dt = forms.DateField(
        label=_('Cancel by'),
        required=False,
        widget=forms.DateInput(attrs={'class':'datepicker'}),
        help_text=_('Date through which cancellation is allowed.')
    )



    class Meta:
        model = RegistrationConfiguration

        fields = (
            'enabled',
            'limit',
            'payment_method',
            'payment_required',
            'external_payment_link',
            'allow_guests',
            'guest_limit',
            'require_guests_info',
            'discount_eligible',
            'gratuity_enabled',
            'gratuity_options',
            'gratuity_custom_option',
            'allow_free_pass',
            'display_registration_stats',
            'use_custom_reg',
            'send_reminder',
            'reminder_days',
            'registration_email_type',
            'registration_email_text',
            'reply_to',
            'reply_to_receive_notices',
            'cancel_by_dt',
            'cancellation_fee',
            'cancellation_percent',
            'cancel_by_dt',
        )

        fieldsets = [(_('Registration Configuration'), {
          'fields': ['enabled',
                    'limit',
                    'payment_method',
                    'payment_required',
                    'external_payment_link',
                    'allow_guests',
                    'guest_limit',
                    'require_guests_info',
                    'discount_eligible',
                    'gratuity_enabled',
                    'gratuity_options',
                    'gratuity_custom_option',
                    'allow_free_pass',
                    'display_registration_stats',
                    'use_custom_reg',
                    'send_reminder',
                    'reminder_days',
                    'registration_email_type',
                    'registration_email_text',
                    'reply_to',
                    'reply_to_receive_notices',
                    'cancellation_fee',
                    'cancellation_percent',
                    'cancel_by_dt',
                    ],
          'legend': ''
          })
        ]
        widgets = {
            'bind_reg_form_to_conf_only': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        reg_form_queryset = kwargs.pop('reg_form_queryset', None)
        self.recurring_edit = kwargs.pop('recurring_edit', False)
        super(Reg8nEditForm, self).__init__(*args, **kwargs)

        #custom_reg_form = CustomRegForm.objects.all()
        reg_form_choices = [('0', '---------')]
        if reg_form_queryset:
            reg_form_choices += [(c.id, c.name) for c in reg_form_queryset]
        if self.instance.id and self.instance.event:
            event_id = self.instance.event.id
        else:
            event_id = None
        self.fields['use_custom_reg'].widget = UseCustomRegWidget(reg_form_choices=reg_form_choices,
                                                                  event_id=event_id)
        # get initial for the field use_custom_reg
        if self.instance.id:
            if self.instance.use_custom_reg_form:
                self.instance.use_custom_reg_form = 1
            else:
                self.instance.use_custom_reg_form = ''
            if self.instance.reg_form:
                reg_form_id = self.instance.reg_form.id
            else:
                reg_form_id = 0
            if self.instance.bind_reg_form_to_conf_only:
                self.instance.bind_reg_form_to_conf_only = 1
            else:
                self.instance.bind_reg_form_to_conf_only = 0
            self.fields['use_custom_reg'].initial = '%s,%s,%s' % \
                                         (str(self.instance.use_custom_reg_form),
                                          str(reg_form_id),
                                          str(self.instance.bind_reg_form_to_conf_only)
                                          )
            reminder_edit_link = '<a href="%s" target="_blank">Edit Reminder Email</a>' % \
                                reverse('event.edit.email', args=[self.instance.event.id])
            if self.instance.event.is_recurring_event:
                message = 'Changes here would be ignored if applied to other events in series.'
                self.fields['use_custom_reg'].help_text = message

            self.fields['reminder_days'].help_text = '%s<br /><br />%s' % \
                                        (self.fields['reminder_days'].help_text,
                                         reminder_edit_link)
            self.fields['registration_email_text'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['use_custom_reg'].initial =',0,1'
            self.fields['registration_email_text'].widget.mce_attrs['app_instance_id'] = 0

        #.short_text_input
        self.fields['reminder_days'].initial = '7,1'
        self.fields['reminder_days'].widget.attrs.update({'class': 'short_text_input'})

        if not get_setting('module', 'corporate_memberships', 'usefreepass'):
            del self.fields['allow_free_pass']

        if not get_setting('module', 'discounts', 'enabled'):
            del self.fields['discount_eligible']

        if self.recurring_edit:
            del self.fields['use_custom_reg']

        # 
        if not settings.EVENTS_GRATUITY_ENABLED:
            del self.fields['gratuity_enabled']
            del self.fields['gratuity_options']
            del self.fields['gratuity_custom_option']
        if not get_setting('module', 'events', 'usethirdpartypayment'):
            del self.fields['external_payment_link']

        # make reply_to a required field
        # Commenting it out because this doesn't work when Registration is not enabled
        #self.fields['reply_to'].required = True
         
        self.add_form_control_class()

    def clean_use_custom_reg(self):
        value = self.cleaned_data['use_custom_reg']
        data_list = value.split(',')

        d = {'use_custom_reg_form': data_list[0],
             'reg_form_id': data_list[1],
             'bind_reg_form_to_conf_only': data_list[2]
             }
        if d['use_custom_reg_form'] == '1' and d['bind_reg_form_to_conf_only'] == '1':
            if d['reg_form_id'] == '0':
                raise forms.ValidationError(_('Please choose a custom registration form'))
        return value

    def clean_gratuity_options(self):
        value = self.cleaned_data['gratuity_options']
        
        for opt in value.split(','):
            is_valid = True
            negative_number = False
            opt = opt.strip().strip('%').strip()
            if '.' in opt:
                head, tail = opt.split('.')
                if not head.isdigit() or not tail.isdigit():
                    is_valid = False
                else:
                    if int(head) < 0:
                        negative_number = True
            else:
                if not opt.isdigit():
                    is_valid = False
                else:
                    if int(opt) < 0:
                        negative_number = True
            if not is_valid:
                raise forms.ValidationError(_("'%(value)s' is not a valid Gratuity options."),
                                            params={'value': opt})
            if negative_number:
                raise forms.ValidationError(_("Invalid Gratuity option '%(value)s'. It should be a positive number."),
                                            params={'value': opt}) 
                
        return value

    def clean_reminder_days(self):
        value = self.cleaned_data['reminder_days']

        if self.cleaned_data.get('send_reminder', False):
            if not value:
                raise forms.ValidationError(_('Please specify when to send email reminders'))
            else:
                days_list = value.split(',')
                new_list = []
                for item in days_list:
                    try:
                        item = int(item)
                        new_list.append(item)
                    except:
                        pass
                if not new_list:
                    raise forms.ValidationError(_("Invalid value '%s'. Integer(s) only. " % value))
        return value

    def save(self, *args, **kwargs):
        # handle three fields here - use_custom_reg_form, reg_form,
        # and bind_reg_form_to_conf_only
        # split the value from use_custom_reg and assign to the 3 fields
        if not self.recurring_edit:
            use_custom_reg_data_list = (self.cleaned_data['use_custom_reg']).split(',')
            try:
                self.instance.use_custom_reg_form = int(use_custom_reg_data_list[0])
            except:
                self.instance.use_custom_reg_form = 0

            try:
                self.instance.bind_reg_form_to_conf_only = int(use_custom_reg_data_list[2])
            except:
                self.instance.bind_reg_form_to_conf_only = 0

            try:
                reg_form_id = int(use_custom_reg_data_list[1])
            except:
                reg_form_id = 0

            if reg_form_id:
                if self.instance.use_custom_reg_form and self.instance.bind_reg_form_to_conf_only:
                    reg_form = CustomRegForm.objects.get(id=reg_form_id)
                    self.instance.reg_form = reg_form
                else:
                    self.instance.reg_form = None
        else:
            if self.instance.use_custom_reg_form == '':
                self.instance.use_custom_reg_form = False

        return super(Reg8nEditForm, self).save(*args, **kwargs)

    # def clean(self):
    #     from django.db.models import Sum

    #     cleaned_data = self.cleaned_data
    #     price_sum = self.instance.regconfpricing_set.aggregate(sum=Sum('price'))['sum']
    #     payment_methods = self.instance.payment_method.all()

    #     print('price_sum', type(price_sum), price_sum)

    #     if price_sum and not payment_methods:
    #         raise forms.ValidationError("Please select possible payment methods for your attendees.")

    #     return cleaned_data




IS_TABLE_CHOICES = (
                    ('0', _('Individual registration(s)')),
                    ('1', _('Table registration')),
                    )


class RegistrationPreForm(forms.Form):
    is_table = forms.ChoiceField(
                    widget=forms.RadioSelect(),
                    choices=IS_TABLE_CHOICES,
                    initial='0'
                                  )

    def __init__(self, table_pricing, *args, **kwargs):
        self.table_only = kwargs.pop('table_only', False)
        super(RegistrationPreForm, self).__init__(*args, **kwargs)
        self.fields['pricing'] = forms.ModelChoiceField(
                    queryset=table_pricing,
                    widget=forms.RadioSelect(),
                    required=False
                    )

        self.fields['pricing'].label_from_instance = _get_price_labels
        self.fields['pricing'].empty_label = None

        if self.table_only:
            del self.fields['is_table']

    def clean_pricing(self):
        if not self.table_only:
            is_table = self.cleaned_data['is_table'] == '1'
        else:
            is_table = True
        pricing = self.cleaned_data['pricing']
        if is_table and not pricing:
            raise forms.ValidationError(_('Please choose a price for table registration.'))

        return pricing


class RegistrationForm(forms.Form):
    """
    Registration form - not include the registrant.
    """
    discount_code = forms.CharField(label=_('Discount Code'), required=False)
    captcha = CustomCatpchaField(label=_('Type the code below'))

    def __init__(self, event, *args, **kwargs):
        """
        event: instance of Event model
        price: instance of RegConfPricing model
        event_price: integer of the event amount
        """
        self.user = kwargs.pop('user', None)
        self.count = kwargs.pop('count', 0)
        super(RegistrationForm, self).__init__(*args, **kwargs)

        reg_conf =  event.registration_configuration

        if not event.free_event and reg_conf.discount_eligible:
            display_discount = True
        else:
            display_discount = False

        if not event.free_event or event.has_addons_price:
            if reg_conf.can_pay_online:
                payment_methods = reg_conf.payment_method.all()
            else:
                payment_methods = reg_conf.payment_method.exclude(
                    machine_name='credit card').order_by('pk')

            if not self.user or self.user.is_anonymous or not self.user.is_superuser:
                payment_methods = payment_methods.exclude(admin_only=True)

            self.fields['payment_method'] = forms.ModelChoiceField(
                empty_label=None, queryset=payment_methods, widget=forms.RadioSelect(), initial=1, required=True)

#            if user and user.profile.is_superuser:
#                self.fields['amount_for_admin'] = forms.DecimalField(decimal_places=2, initial=event_price)
            if event.is_table and not event.free_event:
                if (not self.user.is_anonymous and self.user.is_superuser):
                    self.fields['override_table'] = forms.BooleanField(label=_("Admin Price Override?"),
                                                                 required=False)
                    self.fields['override_price_table'] = forms.DecimalField(label=_("Override Price"),
                                                                max_digits=10,
                                                                decimal_places=2,
                                                                required=False)
                    self.fields['override_price_table'].widget.attrs.update({'size': '5'})

        if not display_discount:
            del self.fields['discount_code']

    def get_discount(self):
        # don't use all() because we don't want to evaluate all items if one of them is false
        if self.is_valid() and hasattr(self.cleaned_data, 'discount_code') and \
                self.cleaned_data['discount_code']:
            try:
                discount = Discount.objects.get(discount_code=self.cleaned_data['discount_code'],
                                                apps__model=RegistrationConfiguration._meta.model_name)
                if discount.available_for(self.count):
                    return discount
            except:
                pass
        return None

    def clean_override_price_table(self):
        override_table = self.cleaned_data['override_table']
        override_price_table = self.cleaned_data['override_price_table']

        if override_table:
            if override_price_table is None:
                raise forms.ValidationError(_('Override is checked, but override price is not specified.'))
            elif  override_price_table < 0:
                raise forms.ValidationError(_('Override price must be a positive number.'))
        return override_price_table


class GratuityForm(forms.Form):
    gratuity = forms.ChoiceField(label=_('Gratuity:'), required=False, choices=[])
    gratuity_preferred = forms.FloatField(label=_('Specify your preferred gratuity:'),
                                          min_value=0, required=False,
                                          help_text=_('Enter a number. For example, 15 for 15%.'))

    def __init__(self, *args, **kwargs):
        self.reg_conf = kwargs.pop('reg_conf')
        super(GratuityForm, self).__init__(*args, **kwargs)
        
        if not self.reg_conf.gratuity_enabled:
            del self.fields['gratuity']
            del self.fields['gratuity_preferred']
        else:
            gratuity_options = self.reg_conf.gratuity_options.split(',')
            gratuity_choices = []
            for opt in gratuity_options:
                gratuity_choices.append((opt.strip('%'), opt))
            self.fields['gratuity'].choices = gratuity_choices
            if not self.reg_conf.gratuity_custom_option:
                del self.fields['gratuity_preferred']
            else:
                self.fields['gratuity_preferred'].widget = PercentWidget()
            
            # add form-control class
            for k in self.fields.keys():
                self.fields[k].widget.attrs['class'] = 'form-control'


class FreePassCheckForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    member_number = forms.CharField(max_length=50, required=False)


class EventTitleChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        event_name = obj.short_name if obj.short_name else obj.title
        return f"{event_name} {obj.start_dt.strftime('%I:%M %p').lstrip('0').replace(':00', '')} - {obj.end_dt.strftime('%I:%M %p').lstrip('0').replace(':00', '')}"
    

class EventCheckInForm(forms.Form):
    """
    Form to change sub-event to check-in registrants to
    """
    def __init__(self, event, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not event.has_child_events_today:
            self.fields['event'] = forms.HiddenInput()
        else:
            current = request.session.get('current_checkin')
            queryset = event.child_events_today
            default = current if current and queryset.filter(pk=current).exists() else queryset.first()
            self.fields['event'] = EventTitleChoiceField(
                queryset=queryset,
                widget=forms.Select,
                initial=default,
                label=_("Check Registrants into Session"),
            )


class ChildEventRegistrationForm(forms.Form):
    """
    Form for child event registration
    """
    def __init__(self, registrant, is_admin, *args, **kwargs):
        super().__init__(*args, **kwargs)

        upcoming_child_events = registrant.registration.event.upcoming_child_events
        # Override constraint to only provide upcoming events if is_admin
        if is_admin:
            upcoming_child_events = registrant.registration.event.child_events.filter(
                registration_configuration__enabled=True
            )

        if not upcoming_child_events.exists():
            return

        # Set the initial values. Add a new control for each session.
        # A session is determined by date and time of the sub-event.
        sub_event_datetimes = registrant.sub_event_datetimes(is_admin)

        for index, start_dt in enumerate(sub_event_datetimes.keys()):
            child_events = upcoming_child_events.filter(start_dt=start_dt)
            choices = [(event.pk, event.title_with_event_code) for event in child_events if not event.at_capacity]
            # Check if registrant already has selection. If so, make sure it's in choices
            selection = None
            current_child_event = registrant.child_events.filter(
                child_event__start_dt=start_dt).first()
            if current_child_event:
                selection = (current_child_event.child_event.pk, current_child_event.child_event.title_with_event_code)
                if selection and selection not in choices:
                    choices.append(selection)

            if not choices:
                continue

            choices.append((None, "Not attending"))
            self.fields[f'{registrant.pk}-{start_dt} - {sub_event_datetimes[start_dt]}'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                required=False,
                label=f'{start_dt.time().strftime("%I:%M %p")} - {sub_event_datetimes[start_dt].time().strftime("%I:%M %p")}',
                help_text=f'{start_dt.date()}'
            )

            # Load current value (if there is one) to allow editing
            if selection:
                self.fields[f'{registrant.pk}-{start_dt} - {sub_event_datetimes[start_dt]}'].initial = selection


class RegistrantForm(FormControlWidgetMixin, AttendanceDatesMixin, forms.Form):
    """
    Registrant form.
    """
    FIELD_NAMES = ['salutation', 'first_name', 'last_name', 'email', 'mail_name',
                   'position_title', 'company_name', 'phone', 'address',
                   'city', 'state', 'zip_code', 'country', 'meal_option',
                   'comments', 'certification_track']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', AnonymousUser)
        self.request = kwargs.pop('request', None)
        self.event = kwargs.pop('event', None)
        self.form_index = kwargs.pop('form_index', None)
        self.pricings = kwargs.pop('pricings', None)
        self.validate_pricing = kwargs.pop('validate_pricing', True)
        self.is_table = kwargs.pop('is_table', False)
        self.default_pricing = kwargs.pop('default_pricing', False)

        if self.event and not self.default_pricing:
            self.default_pricing = getattr(self.event, 'default_pricing', None)

        super(RegistrantForm, self).__init__(*args, **kwargs)

        reg_conf=self.event.registration_configuration
        
        max_length_dict = dict([(field.name, field.max_length) for field in Registrant._meta.fields\
                                if hasattr(field, 'max_length') and field.name in self.FIELD_NAMES])

        # add changes in the stardard registration form
        for field_name in self.FIELD_NAMES:
            if get_setting('module', 'events', 'regform_%s_visible' % field_name):
                field_required = get_setting('module', 'events', 'regform_%s_required' % field_name)
                field_args = {"required": field_required}
                field_type = get_setting('module', 'events', 'regform_%s_type' % field_name)
                if "/" in field_type:
                    field_class, field_widget = field_type.split("/")
                else:
                    field_class, field_widget = field_type, None
                if field_type == 'EmailVerificationField':
                    field_class = EmailVerificationField
                    field_args['label'] = field_name.title()
                else:
                    field_class = getattr(forms, field_class)
                arg_names = field_class.__init__.__code__.co_varnames
                if "max_length" in arg_names:
                    if field_name in max_length_dict:
                        field_args["max_length"] = max_length_dict[field_name]
                    else:
                        field_args["max_length"] = 50
                if "choices" in arg_names:
                    choices = get_setting('module', 'events', 'regform_%s_choices' % field_name)
                    choices = choices.split(",")
                    field_args["choices"] = list(zip(choices, choices))
                if field_widget is not None:
                    module, widget = field_widget.rsplit(".", 1)
                    field_args["widget"] = getattr(import_module(module), widget)
                self.fields[field_name] = field_class(**field_args)

        # add reminder field if event opted to sending reminders to attendees
        if reg_conf.send_reminder:
            self.fields['reminder'] = forms.BooleanField(label=_('Receive event reminders'),
                                                         required=False, initial=True)

        # make the fields in the subsequent forms as not required
        if not reg_conf.require_guests_info:
            if self.form_index and self.form_index > 0:
                for key in self.fields:
                    self.fields[key].required = False
            if not self.event.is_table:
                self.empty_permitted = False
        else:
            self.empty_permitted = False

        # certification field
        if self.event.course:
            cert_choices = self.event.get_certification_choices()
            if cert_choices:
                self.fields['certification_track'] = forms.ChoiceField(
                                label=_('Certification track'),
                                choices = cert_choices,
                                required=False)

        if self.pricings:
            # add the price options field
            self.fields['pricing'] = forms.ModelChoiceField(
                    label='Price Options',
                    queryset=self.pricings,
                    widget=forms.RadioSelect(attrs={'class': 'registrant-pricing'}),
                    initial=self.default_pricing,
                    )
            self.fields['pricing'].label_from_instance = _get_price_labels
            self.fields['pricing'].empty_label = None
            self.fields['pricing'].required=True

        self.add_attendance_dates()

        # member id
        if hasattr(self.event, 'has_member_price') and \
                 get_setting('module', 'events', 'requiresmemberid') and \
                 self.event.has_member_price:
            self.fields['memberid'] = forms.CharField(label=_('Member ID'), max_length=50, required=False,
                                help_text=_('Please enter a member ID if a member price is selected.'))

        if not self.event.is_table and not self.event.free_event:
            if (not self.user.is_anonymous and self.user.is_superuser):
                self.fields['override'] = forms.BooleanField(label=_("Admin Price Override?"),
                                                             required=False)
                self.fields['override_price'] = forms.DecimalField(label=_("Override Price"),
                                                            max_digits=10,
                                                            decimal_places=2,
                                                            required=False)
                self.fields['override_price'].widget.attrs.update({'size': '8'})
        if not self.event.is_table and reg_conf.allow_free_pass:
            self.fields['use_free_pass'] = forms.BooleanField(label=_("Use Free Pass"),
                                                             required=False)
        self.add_form_control_class()

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        # detect markup
        if '<' in data and '>' in data:
            raise forms.ValidationError(_("Markup is not allowed in the name field"))

        # detect URL and Email
        pattern_string = r'\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError(_("URL's and Emails are not allowed in the name field"))

        return data

    def clean_email(self):
        # Removed the email check to allow for multiple
        # registrations
        data = self.cleaned_data['email']
        return data

    def get_user(self, email=None):
        user = None

        if not email:
            email = self.cleaned_data.get('email', '')

        if email:
            [profile] = Profile.objects.filter(user__email__iexact=email,
                                             user__is_active=True,
                                             status=True,
                                             status_detail__iexact='active'
                                             ).order_by('-member_number'
                                            )[:1] or [None]
            if profile:
                user = profile.user

        return user or AnonymousUser()

    def clean_pricing(self):
        pricing = self.cleaned_data['pricing']

        # if pricing allows anonymous, let go.
        if pricing.allow_anonymous:
            return pricing

        if self.validate_pricing:
            # The setting anonymousregistration can be set to 'open', 'validated' and 'strict'
            # Both 'validated' and 'strict' require validation.
            if self.event.anony_setting != 'open':
                # check if user is eligiable for this pricing
                email = self.cleaned_data.get('email', '')
                registrant_user = self.get_user(email)

                if not registrant_user.is_anonymous:
                    if pricing.allow_user:
                        return pricing

                    [registrant_profile] = Profile.objects.filter(user=registrant_user)[:1] or [None]

                    if pricing.allow_member and registrant_profile and registrant_profile.is_member:
                        return pricing

                    if pricing.groups.all():
                        for group in pricing.groups.all():
                            if group.is_member(registrant_user):
                                return pricing

                currency_symbol = get_setting("site", "global", "currencysymbol") or '$'
                err_msg = ""
                redirect_to_403 = False
                if not email:
                    err_msg = 'An email address is required for this price %s%s %s.' \
                                % (currency_symbol, pricing.price, pricing.title)
                else:
                    if pricing.allow_user:
                        # found an inactive user account
                        if User.objects.filter(email__iexact=email, is_active=False).exists():  
                            activation_link = _('<a href="{activate_link}?email={email}&next={next_path}">HERE</a>').format(
                                                    activate_link=reverse('profile.activate_email'),
                                                    email=requests.utils.quote(email),
                                                    next_path=self.request.get_full_path())
                            err_msg = "The email you entered is associated with an inactive account. "
                            inactive_user_err_msg = err_msg + mark_safe(f'''
                                If it is yours, please click {activation_link} and we'll send you an email to activate your account
                                and then you will be returned to here to register this event.''')
                            self.request.user.inactive_user_err_msg = inactive_user_err_msg
                        else:
                            # user doesn't exists in the system
                            err_msg = f'We do not recognize {email} as a site user. Please check your email address or sign up to the site. '
                    else:
                        if pricing.allow_member:
                            err_msg = "We do not recognize %s as a member." % email
                            if len(self.pricings) == 1:
                                redirect_to_403 = True
                                messages.add_message(self.request, messages.ERROR, err_msg)
                        else:
                            if pricing.groups.all():
                                err_msg = "We do not recognize %s as a member of any of the following %s." % (email, ', '.join(pricing.groups.values_list('name', flat=True)))
                        if not err_msg:
                            err_msg = 'Not eligible for the price.%s%s %s.' \
                                        % (currency_symbol, pricing.price, pricing.title)
                        if len(self.pricings) > 1:
                            err_msg += ' Please choose another price option.'
                if redirect_to_403:
                    raise Http403
                raise forms.ValidationError(_(err_msg))

        return pricing

    def clean_memberid(self):
        memberid = self.cleaned_data['memberid']
        pricing = self.cleaned_data.get('pricing', None)
        if not pricing:
            return memberid

        price_requires_member = False

        if pricing.allow_member:
            if not (pricing.allow_anonymous and pricing.allow_user):
                price_requires_member = True

        if price_requires_member:
            if not memberid:
                raise forms.ValidationError(_("We don't detect you as a member. " +
                                            "Please choose another price option. "))
        else:
            if memberid:
                raise forms.ValidationError(_("You have entered a member id but " +
                                            "have selected an option that does not " +
                                            "require membership." +
                                            "Please either choose the member option " +
                                            "or remove your member id."))

        return memberid

    def clean_override_price(self):
        override = self.cleaned_data['override']
        override_price = self.cleaned_data['override_price']
        if override:
            if (override_price is None) or override_price < 0:
                raise forms.ValidationError(_('Override price must be a positive number.'))
        return override_price

    def clean_use_free_pass(self):
        from tendenci.apps.corporate_memberships.utils import get_user_corp_membership
        use_free_pass = self.cleaned_data['use_free_pass']
        email = self.cleaned_data.get('email', '')
        memberid = self.cleaned_data.get('memberid', '')
        corp_membership = get_user_corp_membership(
                                        member_number=memberid,
                                        email=email)
        if use_free_pass:
            if not corp_membership:
                raise forms.ValidationError(_('Not a corporate member for free pass'))
            elif not corp_membership.free_pass_avail:
                raise forms.ValidationError(_('Free pass not available for "%s".' % corp_membership.corp_profile.name))
        return use_free_pass


# extending the BaseFormSet because i want to pass the event obj
# but the BaseFormSet doesn't accept extra parameters
class RegistrantBaseFormSet(BaseFormSet):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        self.request = kwargs.pop('request', None)
        self.is_table = kwargs.pop('is_table', None)
        self.default_pricing = kwargs.pop('default_pricing', None)
        self.validate_pricing = kwargs.pop('validate_pricing', True)
        custom_reg_form = kwargs.pop('custom_reg_form', None)
        if custom_reg_form:
            self.custom_reg_form = custom_reg_form
        pricings = kwargs.pop('pricings', None)
        if pricings:
            self.pricings = pricings
        entries = kwargs.pop('entries', None)
        if entries:
            self.entries = entries
        self.validate_primary_only = get_setting('module', 'events', 'validateprimaryregonly')
        super(RegistrantBaseFormSet, self).__init__(data, files, auto_id, prefix,
                 initial, error_class)

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        If the "Validate Primary Registrant Only" setting is true,
        pricings are only validated for the first form
        """
        defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i)}

        defaults['event'] = self.event
        defaults['user'] = self.user
        defaults['request'] = self.request
        defaults['is_table'] = self.is_table
        #if self.default_pricing:
        defaults['default_pricing'] =self.default_pricing
        defaults['validate_pricing'] = self.validate_pricing
        defaults['form_index'] = i
        if hasattr(self, 'custom_reg_form'):
            defaults['custom_reg_form'] = self.custom_reg_form
        if hasattr(self, 'entries'):
            defaults['entry'] = self.entries[i]
        if hasattr(self, 'pricings'):
            defaults['pricings'] = self.pricings

        # validate pricing on the first registrant only if setting dictates
        if self.validate_primary_only:
            if i != 0:
                defaults['validate_pricing'] = False

        if self.data or self.files:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass

        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        return form

    def _clean_form(self, form):
        email = form.cleaned_data.get('email', None)

        if email:
            if not get_setting('module', 'events', 'canregisteragain'):
                # check if this user can register
                if not self.user.is_superuser:
                    if self.user.is_authenticated and self.user.email.lower() != email.lower():
                        raise forms.ValidationError(_(f"{email} is NOT your email address."))       
                
                # check if this email address is already used
                if Registrant.objects.filter(user__email__iexact=email,
                                             registration__event=self.event,
                                             cancel_dt__isnull=True).exists():
                    if self.user.is_authenticated and email == self.user.email:
                        raise forms.ValidationError(_('You have already registered.'))
                    raise forms.ValidationError(_(f'User {email} has already registered.'))
  
    def clean(self):
        return_data = super(RegistrantBaseFormSet, self).clean()
        # check if we have enough available spaces for price options
        pricings = {}
        for form in self.forms:
            self._clean_form(form)
            pricing = form.cleaned_data.get('pricing', None)
            if pricing and pricing.registration_cap:
                if pricing not in pricings:
                    pricings[pricing] = 1
                else:
                    pricings[pricing] += 1
        for p in pricings:
            if p.spots_available() < pricings[p]:
                raise forms.ValidationError(_('{currency_symbol} {title} - space left {space_available}, but registering {num_registrants}.'.format(
                                                currency_symbol=tcurrency(p.price), 
                                                title=p.title, 
                                                space_available=p.spots_available(),
                                                num_registrants=pricings[p])))

        return return_data



class RegConfPricingBaseModelFormSet(BaseModelFormSet):

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 queryset=None, *, initial=None, **kwargs):
        reg_form_queryset = kwargs.pop('reg_form_queryset', None)
        reg_form_required = kwargs.pop('reg_form_required', None)
        user = kwargs.pop('user', None)
        if reg_form_queryset:
            self.reg_form_queryset = reg_form_queryset
        if reg_form_required:
            self.reg_form_required = reg_form_required
        if user:
            self.user = user
        super(RegConfPricingBaseModelFormSet, self).__init__(data=data, files=files, auto_id=auto_id, prefix=prefix,
                 queryset=queryset, initial=initial, **kwargs)

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        if hasattr(self, 'reg_form_queryset'):
            kwargs['reg_form_queryset'] = self.reg_form_queryset
        if hasattr(self, 'reg_form_required'):
            kwargs['reg_form_required'] = self.reg_form_required
        if hasattr(self, 'user'):
            kwargs['user'] = self.user
        return super(RegConfPricingBaseModelFormSet, self)._construct_form(i, **kwargs)
        

    def clean(self):
        return_data = super(RegConfPricingBaseModelFormSet, self).clean()
        # check and make sure the total of registration limit specified for each pricing
        # not exceed the limit set for this event
        pricing = getattr(self.forms[0], 'instance', None)
        if pricing and hasattr(pricing, 'reg_conf') and pricing.reg_conf:
            limit = pricing.reg_conf.limit
            if limit > 0:
                pricings_total_cap = 0
                for form in self.forms:
                    pricings_total_cap += form.cleaned_data.get('registration_cap', 0)
                if pricings_total_cap > limit:
                    raise forms.ValidationError(_('The registration limit set for this event is {0}, but the total limit specified for each pricing is {1}'.format(limit, pricings_total_cap)))
        return return_data


class MessageAddForm(forms.ModelForm):
    #events = forms.CharField()
    if not settings.USE_BADGES and 'qr_code' in EMAIL_AVAILABLE_TOKENS:
        EMAIL_AVAILABLE_TOKENS.remove('qr_code')
    subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%;padding:5px 0;'}))
    body = forms.CharField(widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Email._meta.app_label,
        'storme_model':Email._meta.model_name.lower()}),
        label=_('Email Content'), help_text=_('Available tokens: <br />' +
        ', '.join(['{{ %s }}' % token for token in EMAIL_AVAILABLE_TOKENS])))

    payment_status = forms.ChoiceField(
        initial='all',
        widget=RadioSelect(),
        choices=(
            ('all',_('All')),
            ('paid',_('Paid')),
            ('not-paid',_('Not Paid')),
    ))

    class Meta:
        model = Email
        fields = ('subject', 'body', 'sender_display', 'reply_to')

    def __init__(self, event_id=None, *args, **kwargs):
        super(MessageAddForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0


class EmailForm(forms.ModelForm):
    #events = forms.CharField()
    if not settings.USE_BADGES and 'qr_code' in EMAIL_AVAILABLE_TOKENS:
        EMAIL_AVAILABLE_TOKENS.remove('qr_code')
    body = forms.CharField(widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Email._meta.app_label,
        'storme_model':Email._meta.model_name.lower()}),
        label=_('Message'), help_text=_('Available tokens: <br />' +
        ', '.join(['{{ %s }}' % token for token in EMAIL_AVAILABLE_TOKENS])))

    class Meta:
        model = Email
        fields = ('reply_to',
                  'sender_display',
                  'subject',
                  'body',)

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0

class PendingEventForm(EventForm):
    primary_group = forms.ModelChoiceField(required=False, queryset=None)

    class Meta:
        model = Event
        fields = (
            'title',
            'description',
            'groups',
            'start_dt',
            'end_dt',
            'on_weekend',
            'timezone',
            'type',
            'external_url',
            'photo_upload',
            'tags',
            )

        fieldsets = [(_('Event Information'), {
                      'fields': ['title',
                                 'description',
                                 'groups',
                                 'start_dt',
                                 'end_dt',
                                 'on_weekend',
                                 'timezone',
                                 'type',
                                 'external_url',
                                 'photo_upload',
                                 'tags',
                                 ],
                      'legend': ''
                      }),
                    ]

    def __init__(self, *args, **kwargs):
        super(PendingEventForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
        self.fields['title'].required = True

        if 'status_detail' in self.fields:
            self.fields.pop('status_detail')
        if 'repeat_type' in self.fields:
            self.fields.pop('repeat_type')
        if 'frequency' in self.fields:
            self.fields.pop('frequency')
        if 'end_recurring' in self.fields:
            self.fields.pop('end_recurring')
        if 'recurs_on' in self.fields:
            self.fields.pop('recurs_on')
        if 'start_event_date' in self.fields:
            self.fields.pop('start_event_date')
        if 'end_event_date' in self.fields:
            self.fields.pop('end_event_date')
        if 'all_day' in self.fields:
            self.fields.pop('all_day')


class AddonForm(FormControlWidgetMixin, BetterModelForm):
    class Meta:
        model = Addon
        fields = ('title',
            'price',
            'description',
            'group',
            'default_yes',
            'position',
            'allow_anonymous',
            'allow_user',
            'allow_member',)
        fieldsets = [
            (_('Addon Information'), {
                'fields': [
                    'title',
                    'price',
                    'description',
                    'group',
                    'default_yes',
                    'position',
                ],'legend': ''
            }),
            (_('Permissions'), {
                'fields': [
                    'allow_anonymous',
                    'allow_user',
                    'allow_member',
                ], 'classes': ['permissions'],
            }),
        ]

class AddonOptionForm(FormControlWidgetMixin, BetterModelForm):
    label = _('Option')

    class Meta:
        model = AddonOption
        fields = ('title',)
        fieldsets = [('', {'fields': ['title']})]


class AddonOptionBaseModelFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(AddonOptionBaseModelFormSet, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False


class EventICSForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class GlobalRegistrantSearchForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.filter(registration__isnull=False).distinct('pk'),
                                   label=_("Event"),
                                   required=False,
                                   empty_label=_('All Events'))
    start_dt = forms.DateField(label=_('Start Date'), required=False)
    end_dt = forms.DateField(label=_('End Date'), required=False)

    user_id = forms.CharField(label=_('User ID'), required=False)
    first_name = forms.CharField(label=_('First Name'), required=False)
    last_name = forms.CharField(label=_('Last Name'), required=False)
    email = forms.CharField(label=_('Email'), required=False)

    def __init__(self, *args, **kwargs):
        super(GlobalRegistrantSearchForm, self).__init__(*args, **kwargs)

        # Set start date and end date
        if self.fields.get('start_dt'):
            self.fields.get('start_dt').widget.attrs = {
                'class': 'datepicker',
            }
        if self.fields.get('end_dt'):
            self.fields.get('end_dt').widget.attrs = {
                'class': 'datepicker',
            }


class EventRegistrantSearchForm(forms.Form):
    SEARCH_METHOD_CHOICES = (
                             ('starts_with', _('Starts With')),
                             ('contains', _('Contains')),
                             ('exact', _('Exact')),
                             )
    SEARCH_CRITERIA_CHOICES = (('', 'SELECT ONE'),
                               ('first_name', _('First Name')),
                               ('last_name', _('Last Name')),
                               ('company_name', _('Company Name')),
                               ('phone', _('Phone')),
                               ('email', _('Email')),)
    search_criteria = forms.ChoiceField(choices=SEARCH_CRITERIA_CHOICES,
                                        required=False)
    search_text = forms.CharField(max_length=100, required=False)
    search_method = forms.ChoiceField(choices=SEARCH_METHOD_CHOICES,
                                        required=False)


class UserMemberRegBaseForm(FormControlWidgetMixin, forms.Form):
    """
    User or member Registration base form.
    """

    def __init__(self, pricings, *args, **kwargs):
        super(UserMemberRegBaseForm, self).__init__(*args, **kwargs)

        self.fields['pricing'] = forms.ModelChoiceField(
            queryset=pricings,
            widget=forms.RadioSelect(),)
        self.fields['pricing'].label_from_instance = _get_price_labels
        self.fields['pricing'].empty_label = None
        self.fields['override'] = forms.BooleanField(label=_("Admin Price Override?"),
                                  required=False)
        self.fields['override_price'] = forms.DecimalField(label=_("Override Price"),
                                            max_digits=10,
                                            decimal_places=2,
                                            required=False)

    def clean_override_price(self):
        override = self.cleaned_data['override']
        override_price = self.cleaned_data['override_price']
        if override:
            if (override_price is None) or override_price < 0:
                raise forms.ValidationError(_('Override price must be a positive number.'))
        return override_price


class AssetsPurchaseForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = AssetsPurchase
        fields = (
            'first_name',
            'last_name',
            'phone',
            'email',
            'pricing',
            'payment_method'
        )

    def __init__(self, event, pricings, *args, **kwargs):
        self.user = kwargs.pop('request_user')
        self.event = event
        reg_conf = event.registration_configuration
        super(AssetsPurchaseForm, self).__init__(*args, **kwargs)

        self.fields['pricing'] = forms.ModelChoiceField(
            queryset=pricings,
            widget=forms.RadioSelect(),)
        self.fields['pricing'].label_from_instance = _get_assets_purchase_price_labels
        self.fields['pricing'].empty_label = None
        if len(pricings) == 1:
            self.fields['pricing'].initial = pricings[0]

        # payment method
        payment_methods = reg_conf.payment_method.all()
        if not self.user.is_superuser:
            payment_methods = payment_methods.exclude(admin_only=True)
        self.fields['payment_method'] = forms.ModelChoiceField(
            empty_label=None, queryset=payment_methods,
            widget=forms.RadioSelect(), initial=1, required=True)

    def clean(self, *args, **kwargs):
        # check if user already purchased
        email = self.cleaned_data['email']
        if AssetsPurchase.objects.filter(email__iexact=email, event_id=self.event.id).exists():
            raise forms.ValidationError(_(f'User with email address "{email}" has purchased already for event {self.event.title}.'))

        return self.cleaned_data


class MemberRegistrationForm(UserMemberRegBaseForm):
    """
    Member Registration form.
    """
    member_ids = forms.CharField(label=_('Member Number'),
                                 help_text=_("comma separated if multiple"))

    def __init__(self, event, pricings, *args, **kwargs):
        super(MemberRegistrationForm, self).__init__(pricings, *args, **kwargs)

    def clean_member_ids(self):
        member_ids = self.cleaned_data['member_ids'].split(',')
        for mem_id in member_ids:
            [member] = Profile.objects.filter(member_number=mem_id.strip(),
                                              status_detail='active')[:1] or [None]
            if not member:
                raise forms.ValidationError(_('Member #%s does not exists!' % mem_id.strip()))

        return self.cleaned_data['member_ids']


class UserRegistrationForm(UserMemberRegBaseForm):
    """
    User Registration form.
    """
    user_display = forms.CharField(max_length=80,
                        label=_('User'),
                        required=False,
                        help_text=_('Type name or username or email, then press the down arrow key to select a suggestion'))
    user = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, event, pricings, *args, **kwargs):
        self.event = event
        super(UserRegistrationForm, self).__init__(pricings, *args, **kwargs)

        self.fields['user'].error_messages['required'
                                ] = _('Please enter a valid user.')

    def clean_user(self):
        user = int(self.cleaned_data['user'])
        if not User.objects.filter(id=user).exists():
            raise forms.ValidationError(_('User does not exists!'))
        if self.event.registrants().filter(user=user):
            user = User.objects.get(id=user)
            raise forms.ValidationError(_(f'{user.first_name} {user.last_name} ({user.email}) already registered for event "{self.event}"!'))

        return self.cleaned_data['user']


class EventExportForm(FormControlWidgetMixin, forms.Form):
    start_dt = forms.DateField(
                label=_('From'),
                initial=datetime.now()-timedelta(days=365))

    end_dt = forms.DateField(
                label=_('To'),
                initial=datetime.now())

    by_type = forms.ModelChoiceField(
                label=_("Filter by Type"),
                queryset=Type.objects.all().order_by('name'),
                empty_label=_("ALL event types"),
                required=False)

    def clean_start_dt(self):
        data = self.cleaned_data
        start_dt = data.get('start_dt')
        if not start_dt:
            raise forms.ValidationError(_('Start date is required'))

        return start_dt

    def clean_end_dt(self):
        data = self.cleaned_data
        start_dt = data.get('start_dt')
        end_dt = data.get('end_dt')

        if not end_dt:
            raise forms.ValidationError(_('End date is required'))
        if end_dt <= start_dt:
            raise forms.ValidationError(_('End date must be greater than start date'))

        return end_dt


class StandardRegAdminForm(forms.Form):

    READONLY_FIELDS =  ['first_name_required', 'first_name_visible',
                        'last_name_required', 'last_name_visible',
                        'email_required', 'email_visible']

    def __init__(self, *args, **kwargs):
        super(StandardRegAdminForm, self).__init__(*args, **kwargs)
        scope = 'module'
        scope_category = 'events'

        regform_settings = Setting.objects.filter(scope=scope, scope_category=scope_category,
                                                  name__startswith="regform_")
        for setting in regform_settings:
            name = setting.name
            field_name = name.split("regform_")[1]
            initial = get_setting('module', 'events', name)
            field_args = {'required':False, 'initial':initial}
            if setting.input_type == 'text':
                self.fields[field_name] = forms.CharField(**field_args)
                self.fields[field_name].widget.attrs['class'] = 'form-control'
            elif setting.input_type == 'select':
                if setting.data_type == 'boolean':
                    self.fields[field_name] = forms.BooleanField(**field_args)
                    if field_name in self.READONLY_FIELDS:
                        self.fields[field_name].widget.attrs['disabled'] = True
                else:
                    try:
                        choices = tuple([(k, v)for k, v in literal_eval(setting.input_value)])
                    except:
                        choices = tuple([(s.strip(), s.strip())for s in setting.input_value.split(',')])
                    field_args['choices'] = choices
                    self.fields[field_name] = forms.ChoiceField(**field_args)
                    self.fields[field_name].widget.attrs['class'] = 'form-control'

    def apply_changes(self):
        cleaned_data = self.cleaned_data
        scope = 'module'
        scope_category = 'events'

        for field_name, value in cleaned_data.items():
            if field_name not in self.READONLY_FIELDS:
                try:
                    setting = Setting.objects.get(scope=scope, scope_category=scope_category,
                                                  name='regform_%s' % field_name)
                except Setting.DoesNotExist:
                    setting = None

                if setting:
                    setting.set_value(value)
                    setting.save()


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + int(month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return date(year,month,day)


class EventReportFilterForm(FormControlWidgetMixin, forms.Form):
    start_dt = forms.SplitDateTimeField(label=_('Start Date/Time'), required=False,
                                        input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
                                        input_time_formats=['%I:%M %p', '%H:%M:%S'])
    end_dt = forms.SplitDateTimeField(label=_('End Date/Time'), required=False,
                                      input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
                                      input_time_formats=['%I:%M %p', '%H:%M:%S'])
    event_type = forms.CharField(required=False,)
    sort_by = forms.ChoiceField(required=False, choices=[('start_dt', _('Start Date')),
                                                         ('groups__name', _('Group Name')),],
                                initial='start_dt')
    sort_direction = forms.ChoiceField(required=False, choices=[('', _('Ascending')),
                                                                ('-', _('Descending')),],
                                       initial='')

    def __init__(self, *args, **kwargs):
        super(EventReportFilterForm, self).__init__(*args, **kwargs)
        now = datetime.now()
        self.initial_start_dt = datetime(now.year, now.month, now.day, 0, 0, 0) - relativedelta(months=1)
        self.initial_end_dt = self.initial_start_dt + relativedelta(months=2)
        self.fields['start_dt'].initial = self.initial_start_dt
        self.fields['end_dt'].initial = self.initial_end_dt
        type_choices = Type.objects.all().order_by('name').values_list('id', 'name')
        self.fields['event_type'].widget = forms.Select(choices=[('','All')] + list(type_choices))
        self.fields['event_type'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        data = self.cleaned_data
        start_dt = data.get('start_dt')
        end_dt = data.get('end_dt')

        if start_dt and end_dt and end_dt < start_dt:
            raise forms.ValidationError(_('End Date/Time should be greater than Start Date/Time.'))

        return data

    def filter(self, queryset=None):
        data = self.cleaned_data
        start_dt = data.get('start_dt')
        if not start_dt:
            start_dt = self.initial_start_dt
        end_dt = data.get('end_dt')
        if not end_dt:
            end_dt = self.initial_end_dt

        if queryset:
            if start_dt and end_dt:
                return queryset.filter(Q(start_dt__gte=start_dt) & Q(start_dt__lte=end_dt))
            else:
                return queryset

        return None
