import re
import imghdr
import calendar
from ast import literal_eval
from os.path import splitext, basename
from datetime import date, datetime, timedelta
from decimal import Decimal

from django import forms
from django.db.models import Q
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms.utils import ErrorList
from importlib import import_module
from django.contrib.auth.models import User, AnonymousUser
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.template.defaultfilters import filesizeformat
from django.conf import settings

from captcha.fields import CaptchaField
from tendenci.apps.events.models import (
    Event, Place, RegistrationConfiguration, Payment,
    Sponsor, Organizer, Speaker, Type, TypeColorSet,
    RegConfPricing, Addon, AddonOption, CustomRegForm,
    CustomRegField, CustomRegFormEntry, CustomRegFieldEntry,
    RecurringEvent
)

from form_utils.forms import BetterModelForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.payments.models import PaymentMethod
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.fields import SplitDateTimeField, EmailVerificationField, CountrySelectField, PriceField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.base.utils import tcurrency
from tendenci.apps.emails.models import Email
from tendenci.apps.files.utils import get_max_file_upload_size
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.site_settings.models import Setting
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import Group
from tendenci.apps.discounts.models import Discount
from tendenci.apps.profiles.models import Profile
from tendenci.apps.events.settings import FIELD_MAX_LENGTH

from fields import UseCustomRegField
from widgets import UseCustomRegWidget

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)

EMAIL_AVAILABLE_TOKENS = ['event_title',
                          'event_date',
                          'event_location',
                          'event_link'
                          ]


SEARCH_CATEGORIES_ADMIN = (
    ('description__icontains', _('Event Description')),
    ('title__icontains', _('Event Title')),
    ('id', 'Event ID'),
    ('place__name__icontains', _('Event Location - Name')),
    ('place__address__icontains', _('Event Location - Address')),
    ('place__city__icontains', _('Event Location - City')),
    ('place__state__icontains', _('Event Location - State')),
    ('tags__icontains', _('Tags')),

    ('priority', _('Priority Events')),

    ('creator__id', _('Creator Userid(#)')),
    ('creator__username', _('Creator Username')),
    ('owner__id', _('Owner Userid(#)')),
    ('owner__username', _('Owner Username')),
)

SEARCH_CATEGORIES = (
    ('description__icontains', _('Event Description')),
    ('title__icontains', _('Event Title')),
    ('id', _('Event ID')),
    ('place__name__icontains', _('Event Location - Name')),
    ('place__address__icontains', _('Event Location - Address')),
    ('place__city__icontains', _('Event Location - City')),
    ('place__state__icontains', _('Event Location - State')),
    ('tags__icontains', _('Tags')),

    ('priority', _('Priority Events')),
)


class EventSearchForm(forms.Form):
    start_dt = forms.CharField(label=_('Start Date/Time'), required=False,
                               widget=forms.TextInput(attrs={'class': 'datepicker'}))
    event_type = forms.ChoiceField(required=False, choices=[])
    event_group = forms.ChoiceField(required=False, choices=[])
    registration = forms.BooleanField(required=False)
    search_category = forms.ChoiceField(choices=SEARCH_CATEGORIES_ADMIN, required=False)
    q = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EventSearchForm, self).__init__(*args, **kwargs)

        if user and not user.is_authenticated():
            del self.fields['registration']
        if user and not user.is_superuser:
            self.fields['search_category'].choices = SEARCH_CATEGORIES

        type_choices = Type.objects.all().order_by('name').values_list('slug', 'name')
        self.fields['event_type'].choices = [('','All')] + list(type_choices)
        
        group_filters = get_query_filters(user, 'groups.view_group', perms_field=False)
        group_choices = Group.objects.filter(group_filters).distinct(
                                        ).order_by('name').values_list('id', 'name')
        self.fields['event_group'].choices = [('','All')] + list(group_choices)

        self.fields['start_dt'].initial = datetime.now().strftime('%Y-%m-%d')

    def clean(self):
        cleaned_data = self.cleaned_data
        q = self.cleaned_data.get('q', None)
        cat = self.cleaned_data.get('search_category', None)

        if cat is None or cat == "" :
            if not (q is None or q == ""):
                self._errors['search_category'] =  ErrorList([_('Select a category')])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                x = int(q)
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
        cleaned_data = self.cleaned_data
        q = self.cleaned_data.get('q', None)
        cat = self.cleaned_data.get('search_category', None)

        if cat is None or cat == "" :
            if not (q is None or q == ""):
                self._errors['search_category'] =  ErrorList([_('Select a category')])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                x = int(q)
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
        cleaned_data = self.cleaned_data
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


class FormForCustomRegForm(forms.ModelForm):

    class Meta:
        model = CustomRegFormEntry
        exclude = ("form", "entry_time")

    def __init__(self, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model
        instance and its related field model instances.
        """
        self.user = kwargs.pop('user', AnonymousUser)
        self.custom_reg_form = kwargs.pop('custom_reg_form', None)
        self.event = kwargs.pop('event', None)
        self.entry = kwargs.pop('entry', None)
        self.form_index = kwargs.pop('form_index', None)
        self.validate_pricing = kwargs.pop('validate_pricing', True)
        self.form_fields = self.custom_reg_form.fields.filter(visible=True).order_by('position')

        self.pricings = kwargs.pop('pricings', None)
        if self.event:
            self.default_pricing = getattr(self.event, 'default_pricing', None)

        super(FormForCustomRegForm, self).__init__(*args, **kwargs)
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
            arg_names = field_class.__init__.im_func.func_code.co_varnames
            if "max_length" in arg_names:
                field_args["max_length"] = FIELD_MAX_LENGTH
            if "choices" in arg_names:
                choices = field.choices.split(",")
                field_args["choices"] = zip(choices, choices)
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
                    for key in self.fields.keys():
                        self.fields[key].required = False
            else:
                # this attr is required for form validation
                self.empty_permitted = False

            # add reminder field if event opted to sending reminders to attendees
            if reg_conf.send_reminder:
                self.fields['reminder'] = forms.BooleanField(label=_('Receive event reminders'),
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

        # member id
        if hasattr(self.event, 'has_member_price') and \
                    get_setting('module', 'events', 'requiresmemberid') and \
                    self.event.has_member_price:
            self.fields['memberid'] = forms.CharField(label=_('Member ID'), required=False,
                                help_text=_('Please enter a member ID if a member price is selected.'))

        # add override and override_price to allow admin override the price
        if hasattr(self.event, 'is_table') and hasattr(self.event, 'free_event'):
            if self.event and not self.event.is_table and not self.event.free_event:
                if (not self.user.is_anonymous() and self.user.profile.is_superuser):
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

                if not registrant_user.is_anonymous():

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
                if not email:
                    err_msg = 'An email address is required for this price %s%s %s. ' % (
                        currency_symbol, pricing.price, pricing.title)
                else:
                    if pricing.allow_user:
                        err_msg = 'We do not detect %s as a site user.' % email
                    else:
                        if pricing.allow_member:
                            err_msg = "We do not detect %s as the member." % email
                        else:
                            if pricing.groups.all():
                                err_msg = "We do not detect %s as a member of any of the following %s." % (email, ', '.join(pricing.groups.values_list('name', flat=True)))
                    if not err_msg:

                        err_msg = 'Not eligible for the price.%s%s %s.' % (
                            currency_symbol,
                            pricing.price,
                            pricing.title,)

                    err_msg += ' Please choose another price option.'
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

        if override and override_price <0:
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
    currency_symbol = get_setting("site", "global", "currencysymbol") or '$'
    if pricing.target_display():
        target_display = ' (%s)' % pricing.target_display()
    else:
        target_display = ''

    end_dt = '<br/>&nbsp;(ends ' + unicode(pricing.end_dt.date()) + ')'
    description = '<br/>&nbsp;' + unicode(pricing.description)

    return mark_safe('&nbsp;<strong><span data-price="%s">%s %s%s</span>%s</strong>%s' % (
                                      pricing.price,
                                      tcurrency(pricing.price),
                                      pricing.title,
                                      target_display,
                                      end_dt,
                                      description) )


# class RadioImageFieldRenderer(forms.widgets.RadioFieldRenderer):

#     def __iter__(self):
#         for i, choice in enumerate(self.choices):
#             yield RadioImageInput(self.name, self.value, self.attrs.copy(), choice, i)

#     def __getitem__(self, idx):
#         choice = self.choices[idx] # Let the IndexError propogate
#         return RadioImageInput(self.name, self.value, self.attrs.copy(), choice, idx)


# class RadioImageInput(forms.widgets.RadioInput):

#     def __unicode__(self):
#         if 'id' in self.attrs:
#             label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
#         else:
#             label_for = ''
#         choice_label = self.choice_label
#         return u'<label%s>%s %s</label>' % (label_for, self.tag(), choice_label)

#     def tag(self):
#         from django.utils.safestring import mark_safe
#         from django.forms.util import flatatt

#         if 'id' in self.attrs:
#             self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
#         final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
#         if self.is_checked():
#             final_attrs['checked'] = 'checked'
#         return mark_safe(u'<input%s />' % flatatt(final_attrs))


class EventForm(TendenciBaseForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Event._meta.app_label,
        'storme_model':Event._meta.model_name.lower()}))

    start_dt = SplitDateTimeField(label=_('Start Date/Time'),
                                  initial=datetime.now()+timedelta(days=30))
    end_dt = SplitDateTimeField(label=_('End Date/Time'),
                                initial=datetime.now()+timedelta(days=30, hours=2))
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
    groups = forms.MultipleChoiceField(required=True, choices=[], help_text=_('Hold down "Control", or "Command" on a Mac, to select more than one.'))

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
        label=_('Ends On'), initial=date.today()+timedelta(days=30),
        widget=forms.DateInput(attrs={'class':'datepicker'}))
    recurs_on = forms.ChoiceField(label=_('Recurs On'), widget=forms.RadioSelect, initial='weekday',
        choices=(('weekday', _('the same day of the week')),('date',_('the same date')),))

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

    class Meta:
        model = Event
        fields = (
            'title',
            'description',
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
            'external_url',
            'photo_upload',
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
                                  'type',
                                  'groups',
                                  'external_url',
                                  'photo_upload',
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
        edit_mode = kwargs.pop('edit_mode', False)
        recurring_mode = kwargs.pop('recurring_mode', False)
        super(EventForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            if 'private_slug' in self.fields.keys():
                self.fields['enable_private_slug'].help_text = self.instance.get_private_slug(absolute_url=True)
            self.fields['start_event_date'].initial = self.instance.start_dt.date()
            self.fields['end_event_date'].initial = self.instance.end_dt.date()
        else:
            # kwargs['instance'] always trumps initial
            if 'private_slug' in self.fields.keys():
                self.fields['private_slug'].initial = self.instance.get_private_slug()
                self.fields['enable_private_slug'].widget = forms.HiddenInput()

            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['groups'].initial = [Group.objects.get_initial_group_id()]

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

        if edit_mode:
            self.fields.pop('is_recurring_event')
            self.fields.pop('repeat_type')
            self.fields.pop('frequency')
            self.fields.pop('end_recurring')
            self.fields.pop('recurs_on')

        if edit_mode and recurring_mode:
            self.fields.pop('start_dt')
            self.fields.pop('end_dt')
            self.fields.pop('start_event_date')
            self.fields.pop('end_event_date')
            self.fields.pop('photo_upload')

        default_groups = Group.objects.filter(status=True, status_detail="active")
        if not self.user.is_superuser:
            filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
            groups = default_groups.filter(filters).distinct()
            groups_list = list(groups.values_list('pk', 'name'))

            users_groups = self.user.profile.get_groups()
            for g in users_groups:
                if [g.id, g.name] not in groups_list:
                    groups_list.append([g.id, g.name])
        else:
            groups_list = default_groups.values_list('pk', 'name')

        self.fields['groups'].choices = groups_list
        self.fields['timezone'].initial = settings.TIME_ZONE

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

    def clean_groups(self):
        group_ids = self.cleaned_data['groups']
        groups = []
        for group_id in group_ids:
            try:
                group = Group.objects.get(pk=group_id)
                groups.append(group)
            except Group.DoesNotExist:
                raise forms.ValidationError(_('Invalid group selected.'))
        return groups

    def clean_end_recurring(self):
        end_recurring = self.cleaned_data.get('end_recurring', None)
        if end_recurring:
            return datetime.combine(end_recurring, datetime.max.time())
        return end_recurring

    def clean(self):
        cleaned_data = self.cleaned_data
        start_dt = cleaned_data.get("start_dt")
        end_dt = cleaned_data.get("end_dt")
        start_event_date = cleaned_data.get('start_event_date')
        end_event_date = cleaned_data.get('end_event_date')

        if start_dt > end_dt:
            errors = self._errors.setdefault("end_dt", ErrorList())
            errors.append(_(u"This cannot be \
                earlier than the start date."))

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
            event.start_dt = datetime.combine(self.cleaned_data.get('start_event_date'), datetime.min.time())
            event.end_dt = datetime.combine(self.cleaned_data.get('end_event_date'), datetime.max.time())

        if self.cleaned_data.get('remove_photo'):
            event.image = None
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

    def __init__(self, queryset, empty_label=u"---------", cache_choices=False,
                 required=True, widget=None, label=None, initial=None, choices=None,
                 help_text=None, to_field_name=None, *args, **kwargs):

        if required and (initial is not None):
            self.empty_label = None
        else:
            self.empty_label = empty_label
        self.cache_choices = cache_choices

        self._choices = ()
        if choices:
            self._choices = choices

        forms.fields.ChoiceField.__init__(self, choices=self._choices, widget=widget)

        self.queryset = queryset
        self.choice_cache = None
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

    class Meta:
        model = Place
        # django 1.8 requires fields or exclude
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        # Populate place
        places = Place.objects.all().order_by(
            'address', 'city', 'state', 'zip', 'country', '-pk').distinct(
            'address', 'city', 'state', 'zip', 'country')

        choices = [('', '------------------------------')]
        for p in places:
            choices.append((p.pk, unicode(p)))
        if self.fields.get('place'):
            self.fields.get('place').choices = choices

        self.fields.keyOrder = [
            'place',
            'name',
            'description',
            'address',
            'city',
            'state',
            'zip',
            'country',
            'url',
        ]
        if self.instance.id:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

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


class SponsorForm(forms.ModelForm):
    label = _('Sponsor')
    class Meta:
        model = Sponsor
        # django 1.8 requires fields or exclude
        exclude = ()


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

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        self.deleted_objects = []
        if not commit:
            self.saved_forms = []
        saved_instances = []

        for form in self.initial_forms:
            pk_name = self._pk_field.name
            raw_pk_value = form._raw_value(pk_name)
            pk_value = form.fields[pk_name].clean(raw_pk_value)
            pk_value = getattr(pk_value, 'pk', pk_value)

            speaker = self._existing_object(pk_value)
            if self.can_delete and self._should_delete_form(form):
                self.deleted_objects.append(speaker)
                continue
            saved_instances.append(self.save_existing(form, speaker, commit=commit))

        new_instances = self.save_new_objects(commit)

        return saved_instances + new_instances


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
        )

        fieldsets = [(_('Speaker'), {
          'fields': ['name',
                    'file',
                    'featured',
                    'description'
                    ],
          'legend': '',
          'classes': ['boxy-grey'],
          })
        ]

    def __init__(self, *args, **kwargs):
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


class OrganizerForm(FormControlWidgetMixin, forms.ModelForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Organizer._meta.app_label,
        'storme_model':Organizer._meta.model_name.lower()}))
    label = 'Organizer'

    class Meta:
        model = Organizer

        fields = (
            'name',
            'description',
        )

    def __init__(self, *args, **kwargs):
        super(OrganizerForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        # django 1.8 requires fields or exclude
        exclude = ()


class Reg8nConfPricingForm(BetterModelForm):
    label = "Pricing"
    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now(), help_text=_('The date time this price starts to be available'))
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=datetime.now()+timedelta(days=30,hours=6), help_text=_('The date time this price ceases to be available'))
    price = PriceField(label=_('Price'), max_digits=21, decimal_places=2, initial=0.00)
    #dates = Reg8nDtField(label=_("Start and End"), required=False)
    groups = forms.MultipleChoiceField(required=False, choices=[])
    payment_required = forms.ChoiceField(required=False,
                                         choices=(('True', _('Yes')), ('False', _('No'))),
                                         initial='True')

    def __init__(self, *args, **kwargs):
        reg_form_queryset = kwargs.pop('reg_form_queryset', None)
        self.user = kwargs.pop('user', None)
        self.reg_form_required = kwargs.pop('reg_form_required', False)
        super(Reg8nConfPricingForm, self).__init__(*args, **kwargs)
        kwargs.update({'initial': {'start_dt':datetime.now(),
                        'end_dt': (datetime(datetime.now().year, datetime.now().month, datetime.now().day, 17, 0, 0)
                        + timedelta(days=29))}})
        #self.fields['dates'].build_widget_reg8n_dict(*args, **kwargs)
        self.fields['allow_anonymous'].initial = True

        default_groups = Group.objects.filter(status=True, status_detail="active")

        if self.user and not self.user.profile.is_superuser:
            filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
            groups = default_groups.filter(filters).distinct()
            groups_list = list(groups.values_list('pk', 'name'))

            users_groups = self.user.profile.get_groups()
            for g in users_groups:
                if [g.id, g.name] not in groups_list:
                    groups_list.append([g.id, g.name])
        else:
            groups_list = list(default_groups.values_list('pk', 'name'))

        groups_list.insert(0, ['', '------------'])
        self.fields['groups'].choices = groups_list

    def clean_groups(self):
        group_list = self.cleaned_data['groups']
        groups = []

        for group_id in group_list:
            if group_id:
                try:
                    group = Group.objects.get(pk=group_id)
                    groups.append(group_id)
                except Group.DoesNotExist:
                    raise forms.ValidationError(_('Invalid group selected.'))

        return Group.objects.filter(pk__in=groups)

    def clean_tax_rate(self):
        tax_rate = self.cleaned_data['tax_rate']
        if tax_rate is None:
            tax_rate = 0
        return tax_rate

    def clean_quantity(self):
        # make sure that quantity is always a positive number
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            quantity = 1
        return quantity


    def clean(self):
        data = self.cleaned_data
        if 'end_dt' in data and data['start_dt'] > data['end_dt']:
            raise forms.ValidationError(_('Start Date/Time should come after End Date/Time'))
        return data

    class Meta:
        model = RegConfPricing

        fields = [
            'title',
            'description',
            'quantity',
            'payment_required',
            'price',
            'include_tax',
            'tax_rate',
            'start_dt',
            'end_dt',
            'groups',
            'allow_anonymous',
            'allow_user',
            'allow_member',
            'position'
         ]

        fieldsets = [(_('Registration Pricing'), {
          'fields': ['title',
                    'description',
                    'quantity',
                    'payment_required',
                    'price',
                    'include_tax',
                    'tax_rate',
                    'start_dt',
                    'end_dt',
                    #'dates',
                    'groups',
                    'allow_anonymous',
                    'allow_user',
                    'allow_member',
                    'position'
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
            _('Registration Limit'),
            initial=0,
            help_text=_("Enter the maximum number of registrants. Use 0 for unlimited registrants")
    )
    payment_method = forms.ModelMultipleChoiceField(
        queryset=PaymentMethod.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=[1,2,3]) # first three items (inserted via fixture)
    use_custom_reg = UseCustomRegField(label="Custom Registration Form")

    registration_email_text = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':RegistrationConfiguration._meta.app_label,
        'storme_model':RegistrationConfiguration._meta.model_name.lower()}))

    class Meta:
        model = RegistrationConfiguration

        fields = (
            'enabled',
            'limit',
            'payment_method',
            'payment_required',
            'require_guests_info',
            'discount_eligible',
            'allow_free_pass',
            'display_registration_stats',
            'use_custom_reg',
            'send_reminder',
            'reminder_days',
            'registration_email_type',
            'registration_email_text',
        )

        fieldsets = [(_('Registration Configuration'), {
          'fields': ['enabled',
                    'limit',
                    'payment_method',
                    'payment_required',
                    'require_guests_info',
                    'discount_eligible',
                    'allow_free_pass',
                    'display_registration_stats',
                    'use_custom_reg',
                    'send_reminder',
                    'reminder_days',
                    'registration_email_type',
                    'registration_email_text',
                    ],
          'legend': ''
          })
        ]
        widgets = {
            'bind_reg_form_to_conf_only': forms.RadioSelect
        }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
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
        return ','.join(data_list)

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

        return super(Reg8nEditForm, self).save(*args, **kwargs)



    # def clean(self):
    #     from django.db.models import Sum

    #     cleaned_data = self.cleaned_data
    #     price_sum = self.instance.regconfpricing_set.aggregate(sum=Sum('price'))['sum']
    #     payment_methods = self.instance.payment_method.all()


    #     print 'price_sum', type(price_sum), price_sum

    #     if price_sum and not payment_methods:
    #         raise forms.ValidationError("Please select possible payment methods for your attendees.")

    #     return cleaned_data


class Reg8nForm(forms.Form):
    """
    Registration form.
    """
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    company_name = forms.CharField(max_length=100, required=False)
    username = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=20, required=False)
    email = EmailVerificationField(label=_("Email"))
    captcha = CaptchaField(label=_('Type the code below'))

    def __init__(self, event_id=None, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(Reg8nForm, self).__init__(*args, **kwargs)

        event = Event.objects.get(pk=event_id)
        payment_method = event.registration_configuration.payment_method.all()

        self.fields['payment_method'] = forms.ModelChoiceField(empty_label=None,
            queryset=payment_method, widget=forms.RadioSelect(), initial=1, required=False)

        self.fields['price'] = forms.DecimalField(
            widget=forms.HiddenInput(), initial=event.registration_configuration.price)

        if user and user.is_authenticated():
            self.fields.pop('captcha')
            user_fields = ['first_name', 'last_name', 'company_name', 'username', 'phone','email']
            for user_field in user_fields:
                self.fields.pop(user_field)

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        # detect markup
        markup_pattern = re.compile('<[^>]*?>', re.I and re.M)
        markup = markup_pattern.search(data)
        if markup:
            raise forms.ValidationError(_("Markup is not allowed in the name field"))

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError(_("URL's and Emails are not allowed in the name field"))

        return data


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
    captcha = CaptchaField(label=_('Type the code below'))

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

        if not event.free_event:
            if reg_conf.can_pay_online:
                payment_methods = reg_conf.payment_method.all()
            else:
                payment_methods = reg_conf.payment_method.exclude(
                    machine_name='credit card').order_by('pk')

            self.fields['payment_method'] = forms.ModelChoiceField(
                empty_label=None, queryset=payment_methods, widget=forms.RadioSelect(), initial=1, required=True)

#            if user and user.profile.is_superuser:
#                self.fields['amount_for_admin'] = forms.DecimalField(decimal_places=2, initial=event_price)
            if event.is_table and not event.free_event:
                if (not self.user.is_anonymous() and self.user.is_superuser):
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

        if override_table and override_price_table <0:
            raise forms.ValidationError(_('Override price must be a positive number.'))
        return override_price_table


class FreePassCheckForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    member_number = forms.CharField(max_length=50, required=False)


class RegistrantForm(forms.Form):
    """
    Registrant form.
    """
    FIELD_NAMES = ['salutation', 'first_name', 'last_name', 'email', 'mail_name',
                   'position_title', 'company_name', 'phone', 'address',
                   'city', 'state', 'zip_code', 'country', 'meal_option',
                   'comments']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', AnonymousUser)
        self.event = kwargs.pop('event', None)
        self.form_index = kwargs.pop('form_index', None)
        self.pricings = kwargs.pop('pricings', None)
        self.validate_pricing = kwargs.pop('validate_pricing', True)

        if self.event:
            self.default_pricing = getattr(self.event, 'default_pricing', None)

        super(RegistrantForm, self).__init__(*args, **kwargs)

        reg_conf=self.event.registration_configuration

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
                arg_names = field_class.__init__.im_func.func_code.co_varnames
                if "max_length" in arg_names:
                    field_args["max_length"] = 100
                if "choices" in arg_names:
                    choices = get_setting('module', 'events', 'regform_%s_choices' % field_name)
                    choices = choices.split(",")
                    field_args["choices"] = zip(choices, choices)
                if field_widget is not None:
                    module, widget = field_widget.rsplit(".", 1)
                    field_args["widget"] = getattr(import_module(module), widget)
                self.fields[field_name] = field_class(**field_args)

        # add reminder field if event opted to sending reminders to attendees
        if reg_conf.send_reminder:
            self.fields['reminder'] = forms.BooleanField(label=_('Receive event reminders'),
                                                         required=False)

        # make the fields in the subsequent forms as not required
        if not reg_conf.require_guests_info:
            if self.form_index and self.form_index > 0:
                for key in self.fields.keys():
                    self.fields[key].required = False
            if not self.event.is_table:
                self.empty_permitted = False
        else:
            self.empty_permitted = False

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

        # member id
        if hasattr(self.event, 'has_member_price') and \
                 get_setting('module', 'events', 'requiresmemberid') and \
                 self.event.has_member_price:
            self.fields['memberid'] = forms.CharField(label=_('Member ID'), required=False,
                                help_text=_('Please enter a member ID if a member price is selected.'))

        if not self.event.is_table and not self.event.free_event:
            if (not self.user.is_anonymous() and self.user.is_superuser):
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


    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        # detect markup
        pattern = re.compile('<[^>]*?>', re.I and re.M)
        markup = pattern.search(data)
        if markup:
            raise forms.ValidationError(_("Markup is not allowed in the name field"))

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
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
            if self.event.anony_setting <> 'open':
                # check if user is eligiable for this pricing
                email = self.cleaned_data.get('email', '')
                registrant_user = self.get_user(email)

                if not registrant_user.is_anonymous():
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
                if not email:
                    err_msg = 'An email address is required for this price %s%s %s.' \
                                % (currency_symbol, pricing.price, pricing.title)
                else:
                    if pricing.allow_user:
                        err_msg = 'We do not detect %s as a site user.' % email
                    else:
                        if pricing.allow_member:
                            err_msg = "We do not detect %s as the member." % email
                        else:
                            if pricing.groups.all():
                                err_msg = "We do not detect %s as a member of any of the following %s." % (email, ', '.join(pricing.groups.values_list('name', flat=True)))
                    if not err_msg:
                        err_msg = 'Not eligible for the price.%s%s %s.' \
                                    % (currency_symbol, pricing.price, pricing.title)
                    err_msg += ' Please choose another price option.'
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
                raise forms.ValidationError(_("We don't detect you as a member. " + \
                                            "Please choose another price option. "))
        else:
            if memberid:
                raise forms.ValidationError(_("You have entered a member id but " + \
                                            "have selected an option that does not " + \
                                            "require membership." + \
                                            "Please either choose the member option " + \
                                            "or remove your member id."))

        return memberid

    def clean_override_price(self):
        override = self.cleaned_data['override']
        override_price = self.cleaned_data['override_price']
        if override and override_price <0:
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

        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True

        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        return form


class RegConfPricingBaseFormSet(BaseFormSet):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, **kwargs):
        reg_form_queryset = kwargs.pop('reg_form_queryset', None)
        reg_form_required = kwargs.pop('reg_form_required', None)
        user = kwargs.pop('user', None)
        if reg_form_queryset:
            self.reg_form_queryset = reg_form_queryset
        if reg_form_required:
            self.reg_form_required = reg_form_required
        if user:
            self.user = user

        super(RegConfPricingBaseFormSet, self).__init__(data, files, auto_id, prefix,
                 initial, error_class)

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i)}

        #defaults['form_index'] = i
        if hasattr(self, 'reg_form_queryset'):
            defaults['reg_form_queryset'] = self.reg_form_queryset
        if hasattr(self, 'reg_form_required'):
            defaults['reg_form_required'] = self.reg_form_required
        if hasattr(self, 'user'):
            defaults['user'] = self.user

        if self.data or self.files:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        return form


class RegConfPricingBaseModelFormSet(BaseModelFormSet):

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 queryset=None, **kwargs):
        # This is nasty, but i only need to replace the BaseFormSet so that we
        # can pass a parameter to our pricing form.
        # Apparently, we don't want to rewrite the entire BaseModelFormSet class.
        # So, here is what we do:
        # 1)  create a class RegConfPricingBaseFormSet - a subclass of BaseFormSet
        # 2)  change the base class of BaseModelFormSet to
        #     RegConfPricingBaseFormSet instead of BaseFormSet
        self.__class__.__bases__[0].__bases__[0].__bases__ = (RegConfPricingBaseFormSet,)
        super(RegConfPricingBaseModelFormSet, self).__init__(data, files, auto_id, prefix,
                 queryset, **kwargs)




class MessageAddForm(forms.ModelForm):
    #events = forms.CharField()
    subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%;padding:5px 0;'}))
    body = forms.CharField(widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Email._meta.app_label,
        'storme_model':Email._meta.model_name.lower()}),
        label=_('Email Content'))

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
        fields = ('subject', 'body',)

    def __init__(self, event_id=None, *args, **kwargs):
        super(MessageAddForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0

class EmailForm(forms.ModelForm):
    #events = forms.CharField()
    body = forms.CharField(widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Email._meta.app_label,
        'storme_model':Email._meta.model_name.lower()}),
        label=_('Message'), help_text=_('Available tokens: <br />' + \
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


class AddonForm(BetterModelForm):
    class Meta:
        model = Addon
        fields = ('title',
            'price',
            'group',
            'allow_anonymous',
            'allow_user',
            'allow_member',)
        fieldsets = [
            (_('Addon Information'), {
                'fields': [
                    'title',
                    'price',
                    'group',
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

class AddonOptionForm(BetterModelForm):
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


class MemberRegistrationForm(forms.Form):
    """
    Member Registration form.
    """
    member_ids = forms.CharField(label=_('Member Number'),
                                 help_text=_("comma separated if multiple"))

    def __init__(self, event, pricings, *args, **kwargs):
        super(MemberRegistrationForm, self).__init__(*args, **kwargs)

        self.fields['pricing'] = forms.ModelChoiceField(
            queryset=pricings,
            widget=forms.RadioSelect(),)
        self.fields['pricing'].label_from_instance = _get_price_labels
        self.fields['pricing'].empty_label = None

    def clean_member_ids(self):
        member_ids = self.cleaned_data['member_ids'].split(',')
        for mem_id in member_ids:
            [member] = Profile.objects.filter(member_number=mem_id.strip(),
                                              status_detail='active')[:1] or [None]
            if not member:
                raise forms.ValidationError(_('Member #%s does not exists!' % mem_id.strip()))

        return self.cleaned_data['member_ids']


class EventExportForm(forms.Form):
    by_date_range = forms.BooleanField(
                label=_('Export by Date Range'),
                required=False)

    start_dt = forms.DateField(
                label=_('From'),
                required=False)

    end_dt = forms.DateField(
                label=_('To'),
                required=False)

    by_type = forms.ModelChoiceField(
                label=_("Export by Type"),
                queryset=Type.objects.all().order_by('name'),
                empty_label=_("Don't filter by type"),
                required=False)

    def clean_start_dt(self):
        data = self.cleaned_data
        by_date_range = data.get('by_date_range')
        start_dt = data.get('start_dt')
        if by_date_range:
            if not start_dt:
                raise forms.ValidationError(_('Start date is required if exporting by date range'))

        return start_dt

    def clean_end_dt(self):
        data = self.cleaned_data

        by_date_range = data.get('by_date_range')
        start_dt = data.get('start_dt')
        end_dt = data.get('end_dt')

        if by_date_range:
            if not end_dt:
                raise forms.ValidationError(_('End date is required if exporting by date range'))
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
            if not field_name in self.READONLY_FIELDS:
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
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return date(year,month,day)


class EventReportFilterForm(forms.Form):
    start_dt = SplitDateTimeField(label=_('Start Date/Time'), required=False)
    end_dt = SplitDateTimeField(label=_('End Date/Time'), required=False)

    def __init__(self, *args, **kwargs):
        super(EventReportFilterForm, self).__init__(*args, **kwargs)
        start_dt = datetime.now()
        end_dt = date.today()
        end_tm = start_dt.time()
        temp_end = add_months(end_dt, 1)
        end_dt = datetime.combine(temp_end, end_tm)

        self.fields['start_dt'].initial = start_dt
        self.fields['end_dt'].initial = end_dt

    def clean(self):
        data = self.cleaned_data
        start_dt = data.get('start_dt')
        end_dt = data.get('end_dt')

        if end_dt < start_dt:
            raise forms.ValidationError(_('End Date/Time should be greater than Start Date/Time.'))

        return data

    def filter(self, queryset=None):
        data = self.cleaned_data
        start_dt = data.get('start_dt')
        end_dt = data.get('end_dt')

        if queryset:
            if start_dt and end_dt:
                return queryset.filter(Q(start_dt__gte=start_dt)&Q(start_dt__lte=end_dt))
            else:
                return queryset

        return None
