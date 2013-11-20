import re
import imghdr
from os.path import splitext, basename
from datetime import date, datetime, timedelta
from decimal import Decimal

from django import forms
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms.util import ErrorList
from django.utils.importlib import import_module
from django.contrib.auth.models import User, AnonymousUser
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.template.defaultfilters import filesizeformat

from captcha.fields import CaptchaField
from tendenci.addons.events.models import (
    Event, Place, RegistrationConfiguration, Payment,
    Sponsor, Organizer, Speaker, Type, TypeColorSet,
    RegConfPricing, Addon, AddonOption, CustomRegForm,
    CustomRegField, CustomRegFormEntry, CustomRegFieldEntry,
    RecurringEvent
)

from form_utils.forms import BetterModelForm
from tinymce.widgets import TinyMCE
from tendenci.core.payments.models import PaymentMethod
from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.core.base.fields import SplitDateTimeField, EmailVerificationField
from tendenci.core.base.widgets import PriceWidget
from tendenci.core.emails.models import Email
from tendenci.core.files.utils import get_max_file_upload_size
from tendenci.core.perms.utils import get_query_filters
from tendenci.core.site_settings.utils import get_setting, get_global_setting
from tendenci.apps.user_groups.models import Group
from tendenci.apps.discounts.models import Discount
from tendenci.apps.profiles.models import Profile
from tendenci.addons.events.settings import FIELD_MAX_LENGTH

from fields import Reg8nDtField, UseCustomRegField
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


class CustomRegFormAdminForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=(('draft', 'Draft'), ('active', 'Active'), ('inactive', 'Inactive')))
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
                    label='Price Options',
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
            self.fields['memberid'] = forms.CharField(label='Member ID', required=False,
                                help_text='Please enter a member ID if a member price is selected.')

        # add override and override_price to allow admin override the price
        if hasattr(self.event, 'is_table') and hasattr(self.event, 'free_event'):
            if self.event and not self.event.is_table and not self.event.free_event:
                if (not self.user.is_anonymous() and self.user.profile.is_superuser):
                    self.fields['override'] = forms.BooleanField(label="Admin Price Override?",
                                                                 required=False)
                    self.fields['override_price'] = forms.DecimalField(label="Override Price",
                                                                max_digits=10,
                                                                decimal_places=2,
                                                                required=False)
                    self.fields['override_price'].widget.attrs.update({'size': '8'})

        if self.event:
            if hasattr(self.event, 'is_table') and hasattr(self.event, 'free_event'):
                if not self.event.is_table and reg_conf.allow_free_pass:
                    self.fields['use_free_pass'] = forms.BooleanField(label="Use Free Pass", required=False)

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

                if pricing.group and pricing.group.is_member(registrant_user):
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
                        if pricing.group:
                            err_msg = "We do not detect %s as a member of %s." % (email, pricing.group.name)
                if not err_msg:

                    err_msg = 'Not eligible for the price.%s%s %s.' % (
                        currency_symbol,
                        pricing.price,
                        pricing.title,)

                err_msg += ' Please choose another price option.'
            raise forms.ValidationError(err_msg)

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
                    raise forms.ValidationError(
                        "We don't detect you as a member. "
                        "Please choose another price option. ")
            else:
                if memberid:
                    raise forms.ValidationError(
                        "You have entered a member id but "
                        "have selected an option that does not "
                        "require membership."
                        "Please either choose the member option "
                        "or remove your member id.")

        return memberid


    def clean_override_price(self):
        override = self.cleaned_data['override']
        override_price = self.cleaned_data['override_price']

        if override and override_price <0:
            raise forms.ValidationError('Override price must be a positive number.')
        return override_price
    
    def clean_use_free_pass(self):
        from tendenci.addons.corporate_memberships.utils import get_user_corp_membership
        use_free_pass = self.cleaned_data['use_free_pass']
        email = self.cleaned_data.get('email', '')
        memberid = self.cleaned_data.get('memberid', '')
        corp_membership = get_user_corp_membership(
                                        member_number=memberid,
                                        email=email)
        if use_free_pass:
            if not corp_membership:
                raise forms.ValidationError('Not a corporate member for free pass')
            elif not corp_membership.free_pass_avail:
                raise forms.ValidationError('Free pass not available for "%s".' % corp_membership.corp_profile.name)
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

    return mark_safe('&nbsp;<span data-price="%s">%s%s %s%s</span>%s' % (
                                      pricing.price,
                                      currency_symbol,
                                      pricing.price,
                                      pricing.title,
                                      target_display,
                                      end_dt) )


class RadioImageFieldRenderer(forms.widgets.RadioFieldRenderer):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioImageInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioImageInput(self.name, self.value, self.attrs.copy(), choice, idx)


class RadioImageInput(forms.widgets.RadioInput):

    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = self.choice_label
        return u'<label%s>%s %s</label>' % (label_for, self.tag(), choice_label)

    def tag(self):
        from django.utils.safestring import mark_safe
        from django.forms.util import flatatt

        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class EventForm(TendenciBaseForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Event._meta.app_label,
        'storme_model':Event._meta.module_name.lower()}))

    start_dt = SplitDateTimeField(label=_('Start Date/Time'),
                                  initial=datetime.now()+timedelta(days=30))
    end_dt = SplitDateTimeField(label=_('End Date/Time'),
                                initial=datetime.now()+timedelta(days=30, hours=2))

    photo_upload = forms.FileField(label=_('Photo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current photo'), required=False)
    group = forms.ChoiceField(required=True, choices=[])

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
        choices=(('weekday', 'the same day of the week'),('date','the same date'),))

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

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
            'on_weekend',
            'timezone',
            'priority',
            'type',
            'group',
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

        fieldsets = [('Event Information', {
                      'fields': ['title',
                                 'description',
                                 'is_recurring_event',
                                 'frequency',
                                 'repeat_type',
                                 'start_dt',
                                 'end_dt',
                                 'recurs_on',
                                 'end_recurring',
                                 ],
                      'legend': ''
                      }),
                      ('Event Information', {
                       'fields': ['on_weekend',
                                  'timezone',
                                  'priority',
                                  'type',
                                  'group',
                                  'external_url',
                                  'photo_upload',
                                  'tags',
                                 ],
                      'legend': ''
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 'enable_private_slug',
                                 'private_slug',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
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
        else:
            # kwargs['instance'] always trumps initial
            if 'private_slug' in self.fields.keys():
                self.fields['private_slug'].initial = self.instance.get_private_slug()
                self.fields['enable_private_slug'].widget = forms.HiddenInput()

            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['group'].initial = Group.objects.get_initial_group_id()

        if self.instance.image:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.image.pk, basename(self.instance.image.file.name))
        else:
            self.fields.pop('remove_photo')
        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        if self.instance.is_recurring_event:
            message = 'Changes here would be ignored if applied to other events in series.'
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
            self.fields.pop('photo_upload')

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
            groups_list = default_groups.values_list('pk', 'name')

        self.fields['group'].choices = groups_list

    def clean_photo_upload(self):
        photo_upload = self.cleaned_data['photo_upload']
        if photo_upload:
            extension = splitext(photo_upload.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo must be of jpg, gif, or png image type.')

            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo is an invalid image. Try uploading another photo.')

            max_upload_size = get_max_file_upload_size()
            if photo_upload.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(photo_upload.size)))

        return photo_upload

    def clean_group(self):
        group_id = self.cleaned_data['group']

        try:
            group = Group.objects.get(pk=group_id)
            return group
        except Group.DoesNotExist:
            raise forms.ValidationError(_('Invalid group selected.'))

    def clean_end_recurring(self):
        end_recurring = self.cleaned_data.get('end_recurring', None)
        if end_recurring:
            return datetime.combine(end_recurring, datetime.max.time())
        return end_recurring

    def clean(self):
        cleaned_data = self.cleaned_data
        start_dt = cleaned_data.get("start_dt")
        end_dt = cleaned_data.get("end_dt")

        if start_dt > end_dt:
            errors = self._errors.setdefault("end_dt", ErrorList())
            errors.append(u"This cannot be \
                earlier than the start date.")

        # Always return the full collection of cleaned data.
        return cleaned_data


    def save(self, *args, **kwargs):
        event = super(EventForm, self).save(*args, **kwargs)

        if self.cleaned_data.get('remove_photo'):
            event.image = None
        return event


class DisplayAttendeesForm(forms.Form):
    display_event_registrants = forms.BooleanField(required=False)
    DISPLAY_REGISTRANTS_TO_CHOICES=(("public","Everyone"),
                                    ("user","Users Only"),
                                    ("member","Members Only"),
                                    ("admin","Admin Only"),)
    display_registrants_to = forms.ChoiceField(choices=DISPLAY_REGISTRANTS_TO_CHOICES,
                                                widget=forms.RadioSelect,
                                                initial='public')
    label = 'Display Attendees'


class ApplyRecurringChangesForm(forms.Form):
    APPLY_CHANGES_CHOICES = (("self","This event only"),
                             ("rest","This and the following events in series"),
                             ("all","All events in series"))
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
            '<img style="width:25px; height:25px" src="/event-logs/colored-image/%s" />'
            % color_set.bg_color) for color_set in colorsets]

        self.fields['color_set'] = TypeChoiceField(
            choices=color_set_choices,
            queryset=colorsets,
            widget=forms.RadioSelect(renderer=RadioImageFieldRenderer),
        )

    class Meta:
        model = Type

class ReassignTypeForm(forms.Form):
    type = forms.ModelChoiceField(empty_label=None, initial=1, queryset=Type.objects.none(), label=_('Reassign To'))

    def __init__(self, *args, **kwargs):
        type_id = kwargs.pop('type_id')
        super(ReassignTypeForm, self).__init__(*args, **kwargs)

        event_types = Type.objects.exclude(pk=type_id)

        self.fields['type'].queryset = event_types


class PlaceForm(forms.ModelForm):
    place = forms.ChoiceField(label=_('Place'), required=False, choices=[])
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': Place._meta.app_label,
        'storme_model': Place._meta.module_name.lower()}))

    label = 'Location Information'

    class Meta:
        model = Place

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
    label = 'Sponsor'
    class Meta:
        model = Sponsor


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


class SpeakerForm(BetterModelForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Speaker._meta.app_label,
        'storme_model':Speaker._meta.module_name.lower()}))
    label = 'Speaker'
    file = forms.FileField(required=False)

    class Meta:
        model = Speaker

        fields = (
            'name',
            'file',
            'featured',
            'description',
        )

        fieldsets = [('Speaker', {
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
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(data.size)))

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


class OrganizerForm(forms.ModelForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Organizer._meta.app_label,
        'storme_model':Organizer._meta.module_name.lower()}))
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


class Reg8nConfPricingForm(BetterModelForm):
    label = "Pricing"
    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=datetime.now()+timedelta(days=30,hours=6))
    dates = Reg8nDtField(label=_("Start and End"), required=False)
    group = forms.ChoiceField(required=False, choices=[])
    payment_required = forms.ChoiceField(required=False,
                            choices=((None,_('Inherit from event')),('True',_('Yes')),('False',_('No'))))

    def __init__(self, *args, **kwargs):
        reg_form_queryset = kwargs.pop('reg_form_queryset', None)
        self.user = kwargs.pop('user', None)
        self.reg_form_required = kwargs.pop('reg_form_required', False)
        super(Reg8nConfPricingForm, self).__init__(*args, **kwargs)
        kwargs.update({'initial': {'start_dt':datetime.now(),
                        'end_dt': (datetime(datetime.now().year, datetime.now().month, datetime.now().day, 17, 0, 0)
                        + timedelta(days=29))}})
        self.fields['dates'].build_widget_reg8n_dict(*args, **kwargs)
        self.fields['allow_anonymous'].initial = True
        self.fields['price'].widget = PriceWidget()

        # skip the field if there is no custom registration forms
        if not reg_form_queryset:
            del self.fields['reg_form']
        else:
            self.fields['reg_form'].queryset = reg_form_queryset
            if self.reg_form_required:
                self.fields['reg_form'].required = True

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
        self.fields['group'].choices = groups_list

    def clean_group(self):
        group_id = self.cleaned_data['group']

        if group_id:
            try:
                group = Group.objects.get(pk=group_id)
                return group
            except Group.DoesNotExist:
                raise forms.ValidationError(_('Invalid group selected.'))


    def clean_quantity(self):
        # make sure that quantity is always a positive number
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            quantity = 1
        return quantity


    def clean(self):
        data = self.cleaned_data
        if 'end_dt' in data and data['start_dt'] > data['end_dt']:
            raise forms.ValidationError('Start Date/Time should come after End Date/Time')
        return data

    class Meta:
        model = RegConfPricing

        fields = [
            'title',
            'quantity',
            'payment_required',
            'price',
            'start_dt',
            'end_dt',
            'reg_form',
            'group',
            'allow_anonymous',
            'allow_user',
            'allow_member',
            'position'
         ]

        fieldsets = [('Registration Pricing', {
          'fields': ['title',
                    'quantity',
                    'payment_required',
                    'price',
                    'dates',
                    'reg_form',
                    'group',
                    'allow_anonymous',
                    'allow_user',
                    'allow_member',
                    'position'
                    ],
          'legend': '',
          'classes': ['boxy-grey'],
          'description': 'Note: the registrants will be verified (for users, ' + \
                        'members or a specific group) if and only if the setting' + \
                        ' <strong>Anonymous Event Registration</strong> is ' + \
                        'set to "validated" or "strict".' + \
                        ' <a href="/settings/module/events/anonymousregistration" ' + \
                        'target="_blank">View or update the setting</a>. '
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


class Reg8nEditForm(BetterModelForm):
    label = 'Registration'
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
        'storme_model':RegistrationConfiguration._meta.module_name.lower()}))

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
            'registration_email_text',
        )

        fieldsets = [('Registration Configuration', {
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

    def clean_use_custom_reg(self):
        value = self.cleaned_data['use_custom_reg']
        data_list = value.split(',')
        if data_list[0] == 'on':
            data_list[0] = '1'
        else:
            data_list[0] = '0'

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
            raise forms.ValidationError("Markup is not allowed in the name field")

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError("URL's and Emails are not allowed in the name field")

        return data


IS_TABLE_CHOICES = (
                    ('0', 'Individual registration(s)'),
                    ('1', 'Table registration'),
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
            raise forms.ValidationError('Please choose a price for table registration.')

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
                    self.fields['override_table'] = forms.BooleanField(label="Admin Price Override?",
                                                                 required=False)
                    self.fields['override_price_table'] = forms.DecimalField(label="Override Price",
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
                                                apps__model=RegistrationConfiguration._meta.module_name)
                if discount.available_for(self.count):
                    return discount
            except:
                pass
        return None


    def clean_override_price_table(self):
        override_table = self.cleaned_data['override_table']
        override_price_table = self.cleaned_data['override_price_table']

        if override_table and override_price_table <0:
            raise forms.ValidationError('Override price must be a positive number.')
        return override_price_table


class FreePassCheckForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    member_number = forms.CharField(max_length=50, required=False)
    

class RegistrantForm(forms.Form):
    """
    Registrant form.
    """
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    company_name = forms.CharField(max_length=100, required=False)
    #username = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=20, required=False)
    email = EmailVerificationField(label=_("Email"))
    comments = forms.CharField(
        max_length=300, widget=forms.Textarea, required=False)

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
            self.fields['memberid'] = forms.CharField(label='Member ID', required=False,
                                help_text='Please enter a member ID if a member price is selected.')

        if not self.event.is_table and not self.event.free_event:
            if (not self.user.is_anonymous() and self.user.is_superuser):
                self.fields['override'] = forms.BooleanField(label="Admin Price Override?",
                                                             required=False)
                self.fields['override_price'] = forms.DecimalField(label="Override Price",
                                                            max_digits=10,
                                                            decimal_places=2,
                                                            required=False)
                self.fields['override_price'].widget.attrs.update({'size': '8'})
        if not self.event.is_table and reg_conf.allow_free_pass:
            self.fields['use_free_pass'] = forms.BooleanField(label="Use Free Pass",
                                                             required=False)


    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        # detect markup
        pattern = re.compile('<[^>]*?>', re.I and re.M)
        markup = pattern.search(data)
        if markup:
            raise forms.ValidationError("Markup is not allowed in the name field")

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError("URL's and Emails are not allowed in the name field")

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

                    if pricing.group and pricing.group.is_member(registrant_user):
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
                            if pricing.group:
                                err_msg = "We do not detect %s as a member of %s." % (email, pricing.group.name)
                    if not err_msg:
                        err_msg = 'Not eligible for the price.%s%s %s.' \
                                    % (currency_symbol, pricing.price, pricing.title)
                    err_msg += ' Please choose another price option.'
                raise forms.ValidationError(err_msg)

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
                raise forms.ValidationError("We don't detect you as a member. " + \
                                            "Please choose another price option. ")
        else:
            if memberid:
                raise forms.ValidationError("You have entered a member id but " + \
                                            "have selected an option that does not " + \
                                            "require membership." + \
                                            "Please either choose the member option " + \
                                            "or remove your member id.")

        return memberid

    def clean_override_price(self):
        override = self.cleaned_data['override']
        override_price = self.cleaned_data['override_price']
        if override and override_price <0:
            raise forms.ValidationError('Override price must be a positive number.')
        return override_price

    def clean_use_free_pass(self):
        from tendenci.addons.corporate_memberships.utils import get_user_corp_membership
        use_free_pass = self.cleaned_data['use_free_pass']
        email = self.cleaned_data.get('email', '')
        memberid = self.cleaned_data.get('memberid', '')
        corp_membership = get_user_corp_membership(
                                        member_number=memberid,
                                        email=email)
        if use_free_pass:
            if not corp_membership:
                raise forms.ValidationError('Not a corporate member for free pass')
            elif not corp_membership.free_pass_avail:
                raise forms.ValidationError('Free pass not available for "%s".' % corp_membership.corp_profile.name)
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
        'storme_model':Email._meta.module_name.lower()}),
        label=_('Email Content'))

    payment_status = forms.ChoiceField(
        initial='all',
        widget=RadioSelect(),
        choices=(
            ('all','All'),
            ('paid','Paid'),
            ('not-paid','Not Paid'),
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
        'storme_model':Email._meta.module_name.lower()}),
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
            'group',
            'start_dt',
            'end_dt',
            'on_weekend',
            'timezone',
            'type',
            'external_url',
            'photo_upload',
            'tags',
            )

        fieldsets = [('Event Information', {
                      'fields': ['title',
                                 'description',
                                 'group',
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

        if 'status_detail' in self.fields:
            self.fields.pop('status_detail')

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
            ('Addon Information', {
                'fields': [
                    'title',
                    'price',
                    'group',
                ],'legend': ''
            }),
            ('Permissions', {
                'fields': [
                    'allow_anonymous',
                    'allow_user',
                    'allow_member',
                ], 'classes': ['permissions'],
            }),
        ]

class AddonOptionForm(forms.ModelForm):
    class Meta:
        model = AddonOption
        fields = ('title',)


class EventICSForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class GlobalRegistrantSearchForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.filter(registration__isnull=False).distinct('pk'),
                                   label=_("Event"),
                                   required=False,
                                   empty_label='All Events')
    start_dt = forms.DateField(label=_('Start Date'), required=False)
    end_dt = forms.DateField(label=_('End Date'), required=False)

    user_id = forms.CharField(label=_('User ID'), required=False)
    first_name = forms.CharField(label=('First Name'), required=False)
    last_name = forms.CharField(label=('Last Name'), required=False)
    email = forms.CharField(label=('Email'), required=False)

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
                                 help_text="comma separated if multiple")

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
                raise forms.ValidationError('Member #%s does not exists!' % mem_id.strip())

        return self.cleaned_data['member_ids']
