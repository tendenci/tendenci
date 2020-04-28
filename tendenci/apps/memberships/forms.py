from builtins import str
import decimal
from datetime import datetime
import requests

from django import forms
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse

from haystack.query import SearchQuerySet
from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.base.fields import EmailVerificationField, PriceField, CountrySelectField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.careers.models import Career
from tendenci.apps.corporate_memberships.models import (CorpMembership, CorpMembershipAuthDomain,)
from tendenci.apps.educations.models import Education
from tendenci.apps.entities.models import Entity
from tendenci.apps.memberships.fields import (
    TypeExpMethodField, NoticeTimeTypeField, MembershipTypeModelChoiceField, DonationOptionAmountField
)
from tendenci.apps.memberships.models import (
    MembershipDefault, MembershipDemographic, MembershipAppField, MembershipType,
    Notice, MembershipImport, MembershipApp, MembershipFile
)
from tendenci.apps.memberships.settings import UPLOAD_ROOT
from tendenci.apps.memberships.utils import (
    get_membership_type_choices, get_corporate_membership_choices, get_selected_demographic_fields,
    get_ud_file_instance, normalize_field_names, get_notice_token_help_text,
)
from tendenci.apps.memberships.widgets import (
    CustomRadioSelect, TypeExpMethodWidget, NoticeTimeTypeWidget, DonationOptionAmountWidget,
)
from tendenci.apps.notifications.utils import send_welcome_email
from tendenci.apps.user_groups.models import Group
from tendenci.apps.payments.fields import PaymentMethodModelChoiceField
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.profiles.models import Profile
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import tcurrency


THIS_YEAR = datetime.today().year

fs = FileSystemStorage(location=UPLOAD_ROOT)

type_exp_method_fields = (
    'period_type', 'period', 'period_unit', 'rolling_option',
    'rolling_option1_day', 'rolling_renew_option', 'rolling_renew_option1_day',
    'rolling_renew_option2_day', 'fixed_option', 'fixed_option1_day',
    'fixed_option1_month', 'fixed_option1_year', 'fixed_option2_day',
    'fixed_option2_month', 'fixed_option2_can_rollover',
    'fixed_option2_rollover_days'
)

type_exp_method_widgets = (
    forms.Select(),
    forms.TextInput(),
    forms.Select(),
    CustomRadioSelect(),
    forms.TextInput(),
    CustomRadioSelect(),
    forms.TextInput(),
    forms.TextInput(),
    CustomRadioSelect(),
    forms.Select(),
    forms.Select(),
    forms.Select(),
    forms.Select(),
    forms.Select(),
    forms.CheckboxInput(),
    forms.TextInput(),
)

CLASS_AND_WIDGET = {
    'text': ('CharField', None),
    'paragraph-text': ('CharField', 'django.forms.Textarea'),
    'check-box': ('BooleanField', None),
    'choose-from-list': ('ChoiceField', None),
    'multi-select': ('MultipleChoiceField', 'django.forms.CheckboxSelectMultiple'),
    'email-field': ('EmailField', None),
    'file-uploader': ('FileField', None),
    'date': ('DateField', 'django.forms.widgets.SelectDateWidget'),
    'date-time': ('DateTimeField', None),
    'membership-type': ('ChoiceField', 'django.forms.RadioSelect'),
    'payment-method': ('ChoiceField', None),
    'first-name': ('CharField', None),
    'last-name': ('CharField', None),
    'email': ('EmailField', None),
    'header': ('CharField', 'tendenci.apps.memberships.widgets.Header'),
    'description': ('CharField', 'tendenci.apps.memberships.widgets.Description'),
    'horizontal-rule': ('CharField', 'tendenci.apps.memberships.widgets.Description'),
    'corporate_membership_id': ('ChoiceField', None),
}


def get_suggestions(entry):
    """
        Generate list of suggestions [people]
        Use the authenticated user that filled out the application
        Use the fn, ln, em mentioned within the application
    """
    user_set = {}

    if entry.user:
        auth_fn = entry.user.first_name
        auth_ln = entry.user.last_name
        auth_un = entry.user.username
        auth_em = entry.user.email
        user_set[entry.user.pk] = '%s %s %s %s' % (auth_fn, auth_ln, auth_un, auth_em)

    if entry.first_name and entry.last_name:
        #mentioned_fn = entry.first_name
        #mentioned_ln = entry.last_name
        mentioned_em = entry.email
    else:
        #mentioned_fn, mentioned_ln, mentioned_em = None, None, None
        mentioned_em = None

    sqs = SearchQuerySet()

#    full_name_q = Q(content='%s %s' % (mentioned_fn, mentioned_ln))
    email_q = Q(content=mentioned_em)
#    q = reduce(operator.or_, [full_name_q, email_q])
    sqs = sqs.filter(email_q)

    sqs_users = [sq.object.user for sq in sqs]

    for u in sqs_users:
        user_set[u.pk] = '%s %s %s %s' % (u.first_name, u.last_name, u.username, u.email)

    user_set[0] = 'Create new user'

    return list(user_set.items())


class MembershipTypeForm(TendenciBaseForm):
    type_exp_method = TypeExpMethodField(label=_('Period Type'))
    description = forms.CharField(label=_('Notes'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows': '3'}))
    price = PriceField(decimal_places=2, help_text=_("Set 0 for free membership."))
    renewal_price = PriceField(decimal_places=2, required=False,
                                 help_text=_("Set 0 for free membership."))
    admin_fee = PriceField(decimal_places=2, required=False,
                           help_text=_("Admin fee for the first time processing"))
    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')), ('inactive', _('Inactive')))
    )

    class Meta:
        model = MembershipType
        fields = (
                  #'app',
                  'name',
                  'price',
                  'admin_fee',
                  'description',
                  #'group',
                  #'period_type',
                  'type_exp_method',
                  'renewal_price',
                  'allow_renewal',
                  'renewal',
                  'never_expires',
                  #'c_period',
                  #'c_expiration_method',
                  #'corporate_membership_only',
                  #'corporate_membership_type_id',
                  'require_approval',
                  'require_payment_approval',
                  'admin_only',
                  'renewal_require_approval',
                  'renewal_period_start',
                  'renewal_period_end',
                  'expiration_grace_period',
                  'position',
                  'status',
                  'status_detail',
                  )

    def __init__(self, *args, **kwargs):
        super(MembershipTypeForm, self).__init__(*args, **kwargs)

        self.type_exp_method_fields = type_exp_method_fields

        initial_list = []
        if self.instance.pk:
            for field in self.type_exp_method_fields:
                field_value = getattr(self.instance, field)
                if field == 'fixed_option2_can_rollover' and (not field_value):
                    field_value = ''
                else:
                    if not field_value:
                        field_value = ''
                initial_list.append(str(field_value))
            self.fields['type_exp_method'].initial = ','.join(initial_list)

        else:
            self.fields['type_exp_method'].initial = "rolling,1,years,0,1,0,1,1,0,1,1,,1,1,,1"

        # a field position dictionary - so we can retrieve data later
        fields_pos_d = {}
        for i, field in enumerate(self.type_exp_method_fields):
            fields_pos_d[field] = (i, type_exp_method_widgets[i])

        self.fields['type_exp_method'].widget = TypeExpMethodWidget(attrs={'id': 'type_exp_method'},
                                                                    fields_pos_d=fields_pos_d)

    def clean(self):
        cleaned_data = self.cleaned_data
        # Make sure Expiretion Grace Period <= Renewal Period End
        expiration_grace_period = self.cleaned_data['expiration_grace_period']
        renewal_period_end = self.cleaned_data['renewal_period_end']
        if expiration_grace_period > renewal_period_end:
            raise forms.ValidationError(_("The Expiration Grace Period should be less than or equal to the Renewal Period End."))
        return cleaned_data


    def clean_expiration_grace_period(self):
        value = self.cleaned_data['expiration_grace_period']
        if value > 100:
            raise forms.ValidationError(_("This number should be less than 100 (days)."))
        return value

    def clean_type_exp_method(self):
        value = self.cleaned_data['type_exp_method']

        # if never expires is checked, no need to check further
        if self.cleaned_data['never_expires']:
            return value

        data_list = value.split(',')
        d = dict(zip(self.type_exp_method_fields, data_list))
        if d['period_type'] == 'rolling':
            if d['period']:
                try:
                    d['period'] = int(d['period'])
                except:
                    raise forms.ValidationError(_("Period must be a numeric number."))
            else:
                raise forms.ValidationError(_("Period is a required field."))
            try:
                d['rolling_option'] = int(d['rolling_option'])
            except:
                raise forms.ValidationError(_("Please select a expiration option for join."))
            if d['rolling_option'] not in [0, 1]:
                raise forms.ValidationError(_("Please select a expiration option for join."))
            if d['rolling_option'] == 1:
                try:
                    d['rolling_option1_day'] = int(d['rolling_option1_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in option 2 of Expires On must be a numeric number."))
            # renew expiration
            try:
                d['rolling_renew_option'] = int(d['rolling_renew_option'])
            except:
                raise forms.ValidationError(_("Please select a expiration option for renewal."))
            if d['rolling_renew_option'] not in [0, 1, 2]:
                raise forms.ValidationError(_("Please select a expiration option for renewal."))
            if d['rolling_renew_option'] == 1:
                try:
                    d['rolling_renew_option1_day'] = int(d['rolling_renew_option1_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in option 2 of Renew Expires On must be a numeric number."))
            if d['rolling_renew_option'] == 2:
                try:
                    d['rolling_renew_option2_day'] = int(d['rolling_renew_option2_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in option 3 of Renew Expires On must be a numeric number."))

        else:  # d['period_type'] == 'fixed'
            try:
                d['fixed_option'] = int(d['fixed_option'])
            except:
                raise forms.ValidationError(_("Please select an option for fixed period."))
            if d['fixed_option'] not in [0, 1]:
                raise forms.ValidationError(_("Please select an option for fixed period."))
            if d['fixed_option'] == 0:
                try:
                    d['fixed_option1_day'] = int(d['fixed_option1_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in the option 1 of Expires On must be a numeric number."))
            if d['fixed_option'] == 1:
                try:
                    d['fixed_option2_day'] = int(d['fixed_option2_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in the option 2 of Expires On must be a numeric number."))

            if 'fixed_option2_can_rollover' in d:
                try:
                    d['fixed_option2_rollover_days'] = int(d['fixed_option2_rollover_days'])
                except:
                    raise forms.ValidationError(_("The grace period day(s) for optoin 2 must be a numeric number."))

        return value

    def save(self, *args, **kwargs):
        return super(MembershipTypeForm, self).save(*args, **kwargs)


class MembershipDefaultUploadForm(forms.ModelForm):
    KEY_CHOICES = (
        ('username', 'username'),
        ('email', 'email'),
        ('member_number', 'member_number'),
        ('email/member_number', 'email then member_number'),
        ('member_number/email', 'member_number then email'),
        ('email/member_number/fn_ln_phone',
         'email/member_number/first_name,last_name,phone'),
        ('member_number/email/fn_ln_phone',
         'member_number/email/first_name,last_name,phone'),
        )
    interactive = forms.HiddenInput()
    key = forms.ChoiceField(label=_("Key"),
                            choices=KEY_CHOICES)

    class Meta:
        model = MembershipImport
        fields = (
                'key',
                'override',
                'interactive',
                'upload_file',
                  )

    def __init__(self, *args, **kwargs):
        super(MembershipDefaultUploadForm, self).__init__(*args, **kwargs)
        self.fields['interactive'].initial = 1
        self.fields['interactive'].widget = forms.HiddenInput()
        self.fields['key'].initial = 'email/member_number/fn_ln_phone'

    def clean_upload_file(self):
        key = self.cleaned_data['key']
        upload_file = self.cleaned_data['upload_file']
        if not key:
            raise forms.ValidationError(_('Please specify the key to identify duplicates'))

        file_content = upload_file.read().decode("utf-8")
        upload_file.seek(0)
        header_line_index = file_content.find('\n')
        header_list = ((file_content[:header_line_index]
                            ).strip('\r')).split(',')
        header_list = normalize_field_names(header_list)
        key_list = []
        for key in key.split('/'):
            if key == 'fn_ln_phone':
                key_list.extend(['first_name', 'last_name', 'phone'])
            else:
                key_list.append(key)
        missing_columns = []
        for item in key_list:
            if item not in header_list:
                missing_columns.append(item)
        if missing_columns:
            msg_string = """
                        'Field(s) %s used to identify the duplicates
                        should be included in the .csv file.'
                        """ % (', '.join(missing_columns))
            raise forms.ValidationError(_(msg_string))

        return upload_file


class MembershipAppForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': MembershipApp._meta.app_label,
        'storme_model': MembershipApp._meta.model_name.lower()}))

    confirmation_text = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': MembershipApp._meta.app_label,
        'storme_model': MembershipApp._meta.model_name.lower()}))

    status_detail = forms.ChoiceField(
        choices=(
            ('draft', _('Draft')),
            ('published', _('Published')),
            ('inactive', _('Inactive'))
        ),
        initial='published'
    )

    donation_label = forms.CharField(label=_("Label"), required=False,
                                     initial=_("Select or specify your contribution"),)
    donation_default_amount = PriceField(label=_("Default Amount"), decimal_places=2,
                                         help_text=_("Set a default amount for donation."),
                                         initial=35)
#    app_field_selection = AppFieldSelectionField(label='Select Fields')

    class Meta:
        model = MembershipApp
        fields = (
            'name',
            'slug',
            'description',
            'confirmation_text',
            'notes',
            'membership_types',
            'include_tax',
            'tax_rate',
            'donation_enabled',
            'donation_label',
            'donation_default_amount',
            'payment_methods',
            'use_for_corp',
            'use_captcha',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status_detail',
            'discount_eligible',
            'allow_multiple_membership',
#            'app_field_selection',
            )

    def __init__(self, *args, **kwargs):
        super(MembershipAppForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs[
                            'app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

        if self.instance.pk:
            self.fields['confirmation_text'].widget.mce_attrs[
                            'app_instance_id'] = self.instance.pk
        else:
            self.fields['confirmation_text'].widget.mce_attrs[
                                    'app_instance_id'] = 0


class AutoRenewSetupForm(forms.Form):
    selected_m = forms.MultipleChoiceField(choices=[], error_messages={'required':_('Please select one')})

    def __init__(self, *args, **kwargs):
        memberships = kwargs.pop('memberships')
        super(AutoRenewSetupForm, self).__init__(*args, **kwargs)
        self.fields['selected_m'].choices = [(m.id, m.id) for m in memberships]


class MembershipAppFieldAdminForm(forms.ModelForm):
    class Meta:
        model = MembershipAppField
        fields = (
                'membership_app',
                'label',
                'field_name',
                'required',
                'display',
                'admin_only',
                'field_type',
                'description',
                'help_text',
                'choices',
                'default_value',
                'css_class'
                  )

    def __init__(self, *args, **kwargs):
        super(MembershipAppFieldAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            if not self.instance.field_name:
                self.fields['field_type'].choices = MembershipAppField.FIELD_TYPE_CHOICES2
            else:
                self.fields['field_type'].choices = MembershipAppField.FIELD_TYPE_CHOICES1

    def save(self, *args, **kwargs):
        self.instance = super(MembershipAppFieldAdminForm, self).save(*args, **kwargs)
        if self.instance:
            if not self.instance.field_name:
                if self.instance.field_type != 'section_break':
                    self.instance.field_type = 'section_break'
                    self.instance.save()
            else:
                if self.instance.field_type == 'section_break':
                    self.instance.field_type = 'CharField'
                    self.instance.save()
        return self.instance


field_size_dict = {
        'initials': 12,
        'displayname': 36,
        'company': 36,
        'department': 20,
        'city': 24,
        'state': 12,
        'country': 14,
        'zipcode': 24,
        'phone': 22,
        'phone2': 22,
        'work_phone': 22,
        'fax': 22,
        'primary_practive': 75,
        'networking': 30,
        'government_agency': 50,
        'company_size': 5,
        'referral_source_member_name': 40,
        'referral_source_other': 28,
        'referral_source_member_number': 20,
        'member_number': 15,
        'application_approved_denied_user': 10,
        'application_complete_user': 10,
        'license_state': 10,
        'network_sectors': 35,
        'website': 36,
        'affiliation_member_number': 30,
        'how_long_in_practice': 5,
        'license_number': 15,
        'url': 36,
        'url2': 36,
        'sex': 20,
        'username': 20,
        'home_state': 10,
        'address2': 15
                   }


def get_field_size(app_field_obj):
    return field_size_dict.get(app_field_obj.field_name, '') or 28


def assign_fields(form, app_field_objs):
    # a list of names of app fields
    field_names = [field.field_name for field in app_field_objs
                   if field.field_name != '' and
                   field.field_name in form.fields]

    for name in list(form.fields):
        if name not in field_names and name != 'discount_code':
            del form.fields[name]
    # update the field attrs - label, required...
    for obj in app_field_objs:
        obj.display_only = False
        if obj.field_name in field_names:
            if obj.field_type and obj.field_name not in [
                                    'payment_method',
                                    'membership_type',
                                    'groups',
                                    'status',
                                    'status_detail',
                                    'directory',
                                    'industry',
                                    'region']:
                # create form field with customized behavior
                field = obj.get_field_class(
                        initial=form.fields[obj.field_name].initial)
                if obj.default_value is not None and obj.default_value != '':
                    field.initial = obj.default_value
                form.fields[obj.field_name] = field
            else:
                field = form.fields[obj.field_name]
                field.label = obj.label
                field.required = obj.required

            obj.field_stype = field.widget.__class__.__name__.lower()

            if obj.field_stype == 'textinput':
                size = get_field_size(obj)
                field.widget.attrs.update({'size': size})
            elif obj.field_stype == 'datetimeinput':
                field.widget.attrs.update({'class': 'datepicker'})
            elif 'selectdatewidget' in obj.field_stype:
                field.widget.years = list(range(1920, THIS_YEAR + 10))
            label_type = []
            if obj.field_name not in ['payment_method',
                                      'membership_type',
                                      'groups'] \
                    and obj.field_stype not in [
                        'radioselect',
                        'checkboxselectmultiple']:
                obj.field_div_class = 'inline-block'
                label_type.append('inline-block')
                if len(obj.label) < 16:
                    label_type.append('short-label')
                    if obj.field_stype == 'textarea':
                        label_type.append('float-left')
                        obj.field_div_class = 'float-left'
            else:
                obj.field_div_class = ''
            obj.label_type = ' '.join(label_type)


class UserForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, app_field_objs, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.is_corp_rep = kwargs.pop('is_corp_rep', None)
        super(UserForm, self).__init__(*args, **kwargs)

        del self.fields['groups']

        assign_fields(self, app_field_objs)
        self_fields_keys = list(self.fields.keys())

        self.is_renewal = 'username' in self.request.GET
        if (self.request.user.is_superuser and self.is_renewal) or (self.instance and self.instance.pk):
            if 'username' in self_fields_keys:
                self_fields_keys.remove('username')
            if 'password' in self_fields_keys:
                self_fields_keys.remove('password')
            if 'username' in self.fields:
                self.fields.pop('username')
            if 'password' in self.fields:
                self.fields.pop('password')

        if 'password' in self_fields_keys:
            passwd = app_field_objs.filter(field_name='password')[0]
            self.fields['password'] = forms.CharField(
                initial=u'',
                label=passwd.label,
                widget=forms.PasswordInput,
                required=False,
                help_text=passwd.help_text
            )
            self.fields['password'].widget.attrs.update({'size': 28})

            self.fields['confirm_password'] = forms.CharField(
                initial=u'',
                label=_("Confirm password"),
                widget=forms.PasswordInput,
                required=False,
            )
            self.fields['confirm_password'].widget.attrs.update({'size': 28})

        if 'username' in self_fields_keys:
            username = app_field_objs.filter(field_name='username')[0]
            self.fields['username'] = forms.RegexField(regex=r'^[\w.@+-]+$',
                                required=False,
                                max_length=30,
                                widget=forms.TextInput,
                                label=username.label,
                                help_text=username.help_text,
                                error_messages = {
                                    'invalid' : _("Allowed characters are letters, digits, at sign (@), period (.), plus sign (+), dash (-), and underscore (_).")
                                })

        self.field_names = [name for name in self.fields]
        self.add_form_control_class()

    def clean(self):
        """
        Validating username and password fields.

        Neither username or password is required.
        If the field(s) are submitted, those fields
        are tested and exceptions are raised if they fail.

        Possible exceptions:
            Passwords do not match
            Username and password did not match
            This username exists. If it's yours,
                please provide a password.
        """
        # super(UserForm, self).clean()

        data = self.cleaned_data

        un = data.get('username', u'').strip()
        pw = data.get('password', u'').strip()
        pw_confirm = data.get('confirm_password', u'').strip()
        email = data.get('email', u'').strip()
        u = None
        login_link = _('click <a href="/accounts/login/?next=%s">HERE</a> to log in before completing your application.') % self.request.get_full_path()
        username_validate_err_msg = mark_safe(_('This Username already exists in the system. If this is your Username, %s Else, select a new Username to continue.') % login_link)
        email_validate_err_msg = mark_safe(_('This Email address already exists in the system. If this is your Email address, %s Else, select a different Email address to continue.') % login_link)
        activation_link = _('<a href="{activate_link}?username={username}&email={email}&next={next_path}">HERE</a>').format(
                                                    activate_link=reverse('profile.activate_email'),
                                                    username=requests.utils.quote(un), email=requests.utils.quote(email),
                                                    next_path=self.request.get_full_path())
        inactive_user_err_msg =  mark_safe(_('''This email "{email}" is associated with previous site activity.
                    Please click {activation_link} and we'll send you an email to activate your account and then you
                    will be returned to this application.''').format(email=email, activation_link=activation_link))

        if self.request.user.is_authenticated and self.request.user.username == un:
            # they are logged in and join or renewal for themselves
            if email and email !=  self.request.user.email:
                # email is changed
                if User.objects.filter(email=email).exists():
                    raise forms.ValidationError(_('''This Email address "%s" already exists in the system.
                                    Please select a different one to continue.''') % email)

        else:
            if un and pw:
                # assert passwords match
                if pw != pw_confirm:
                    raise forms.ValidationError(
                        _('Passwords do not match.')
                    )

                [u] = User.objects.filter(username=un)[:1] or [None]

                if u and u.is_active:
                    # assert password;
                    if not u.check_password(pw):
                        raise forms.ValidationError(username_validate_err_msg)
                else:
                    if u:
                        # user is not active. if email matches, let them activate the account.
                        if email and u.email == email:
                            raise forms.ValidationError(inactive_user_err_msg)
                        raise forms.ValidationError('This username is taken. Please choose a new username.')

            elif un:
                [u] = User.objects.filter(username=un)[:1] or [None]
                # assert username
                if u:
                    raise forms.ValidationError(
                        _('This username exists. If it\'s yours, please provide your password.')
                    )

            if not u and not self.is_renewal:
                # we didn't find user, check if email address is already in use
                if un and email:
                    if User.objects.filter(email=email).exists():
                        if self.request.user.is_authenticated:
                            # user is logged in
                            raise forms.ValidationError(_('This email "%s" is taken. Please check username or enter a different email address.') % email)

                        # user is not logged in. prompt them to log in if the user record with this email address is active
                        u = User.objects.filter(email=email).order_by('-is_active')[0]
                        [profile] = Profile.objects.filter(user=u)[:1] or [None]
                        if (profile and profile.is_active) or u.is_active:
                            raise forms.ValidationError(email_validate_err_msg)

                        # at this point, user is not logged in and user record with this email is inactive
                        # let them activate the account before applying for membership
                        raise forms.ValidationError(inactive_user_err_msg)

        return data

    def save(self, **kwargs):
        """
        Get or create (user and profile) object
        """
        kwargs['commit'] = False
        super(UserForm, self).save(**kwargs)

        user_attrs = {
            'username': self.cleaned_data.get('username'),
            'password': self.cleaned_data.get('password'),
            'email': self.cleaned_data.get('email'),
            'first_name': self.cleaned_data.get('first_name'),
            'last_name': self.cleaned_data.get('last_name'),
        }
        if not user_attrs['password']:
            user_attrs['password'] = User.objects.make_random_password(length=8)

        # all fields are required in order to pull
        # an existing user record
        if all(user_attrs.values()):
            user, created = User.objects.get_or_create(username=user_attrs['username'])
            user.set_password(user_attrs['password'])
            user.email = user.email or user_attrs['email']
            user.first_name = user.first_name or user_attrs['first_name']
            user.last_name = user.last_name or user_attrs['last_name']
        elif self.request.user.is_authenticated and \
                not (self.request.user.is_superuser or self.is_corp_rep):
            created = False
            user = self.request.user
            user.email = user.email or user_attrs['email']
            user.first_name = user.first_name or user_attrs['first_name']
            user.last_name = user.last_name or user_attrs['last_name']
        elif User.objects.filter(email=user_attrs['email']).exists():
            created = False
            user = User.objects.filter(email=user_attrs['email']).order_by('-last_login')[0]
            user.first_name = user.first_name or user_attrs['first_name']
            user.last_name = user.last_name or user_attrs['last_name']
        else:
            created = True
            user_attrs['username'] = user_attrs['username'] or \
                Profile.spawn_username(user_attrs['first_name'][:1], user_attrs['last_name'])

            user = User.objects.create_user(
                username=user_attrs['username'],
                email=user_attrs['email'],
                password=user_attrs['password'])

            user.first_name = user_attrs['first_name']
            user.last_name = user_attrs['last_name']

        if created:
            user.is_active = False
        user.save()

        return user


class ProfileForm(FormControlWidgetMixin, forms.ModelForm):
    country = CountrySelectField(label=_('Country'), required=False)
    country_2 = CountrySelectField(label=_('Country'), required=False)
    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, app_field_objs, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        del self.fields['referral_source']

        assign_fields(self, app_field_objs)
        self.field_names = [name for name in self.fields]

        self.add_form_control_class()

    def save(self, *args, **kwargs):
        """
        Save the profile record. Populate owner and creator fields.
        """
        request_user = kwargs.pop('request_user')

        kwargs['commit'] = False
        profile = super(ProfileForm, self).save(*args, **kwargs)

        for k, v in self.cleaned_data.items():

            if v:
                if hasattr(profile, k) and isinstance(v, str):
                    v = v.strip() or getattr(profile, k)
                setattr(profile, k, v)

        if not request_user.is_anonymous:
            profile.owner = request_user
            profile.owner_username = request_user.username

        profile.save()

        return profile


YEAR_CHOICES = [(i, i) for i in range(1900, THIS_YEAR + 50)]
YEAR_CHOICES = [(0, '?')] + YEAR_CHOICES
class EducationForm(FormControlWidgetMixin, forms.Form):

    school1 = forms.CharField(label=_('School'), max_length=200, required=False, initial='')
    major1 = forms.CharField(label=_('Major'), max_length=200, required=False, initial='')
    degree1 = forms.CharField(label=_('Degree'), max_length=200, required=False, initial='')
    graduation_dt1 = forms.ChoiceField(label=_('Graduation Year'), required=False, choices=YEAR_CHOICES)
    school2 = forms.CharField(label=_('School 2'), max_length=200, required=False, initial='')
    major2 = forms.CharField(label=_('Major 2'), max_length=200, required=False, initial='')
    degree2 = forms.CharField(label=_('Degree 2'), max_length=200, required=False, initial='')
    graduation_dt2 = forms.ChoiceField(label=_('Graduation Year 2'), required=False, choices=YEAR_CHOICES)
    school3 = forms.CharField(label=_('School 3'), max_length=200, required=False, initial='')
    major3 = forms.CharField(label=_('Major 3'), max_length=200, required=False, initial='')
    degree3 = forms.CharField(label=_('Degree 3'), max_length=200, required=False, initial='')
    graduation_dt3 = forms.ChoiceField(label=_('Graduation Year 3'), required=False, choices=YEAR_CHOICES)
    school4 = forms.CharField(label=_('School 4'), max_length=200, required=False, initial='')
    major4 = forms.CharField(label=_('Major 4'), max_length=200, required=False, initial='')
    degree4 = forms.CharField(label=_('Degree 4'), max_length=200, required=False, initial='')
    graduation_dt4 = forms.ChoiceField(label=_('Graduation Year 4'), required=False, choices=YEAR_CHOICES)

    def __init__(self, app_field_objs, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EducationForm, self).__init__(*args, **kwargs)
        self.blank_form = False
        if user:
            self.user = user
        else:
            self.user = None
        if app_field_objs:
            assign_fields(self, app_field_objs)
        self.field_names = [name for name in self.fields]
        
        # If none Education fields are presented on the form, clear fields from the
        # EducationForm to prevent the existing education data from being wipped out.
        if app_field_objs and app_field_objs.filter(field_name__in=['school1', 'major1', 'degree1', 'graduation_dt1',
            'school2', 'major2', 'degree2', 'graduation_dt2',
            'school3', 'major3', 'degree3', 'graduation_dt3',
            'school4', 'major4', 'degree4', 'graduation_dt4']).count() == 0:
            self.fields.clear()
            self.blank_form = True
            return

        if self.user:
            education_list = self.user.educations.all().order_by('pk')[0:4]
            if education_list.exists():
                cnt = 1
                for education in education_list:
                    field_key = 'school%s' % cnt
                    if field_key in self.fields:
                        self.fields[field_key].initial = education.school
                    field_key = 'major%s' % cnt
                    if field_key in self.fields:
                        self.fields[field_key].initial = education.major
                    field_key = 'degree%s' % cnt
                    if field_key in self.fields:
                        self.fields[field_key].initial = education.degree
                    field_key = 'graduation_dt%s' % cnt
                    if field_key in self.fields:
                        self.fields[field_key].initial = education.graduation_year
                    cnt += 1

        self.add_form_control_class()

    def save(self, user):
        if self.blank_form:
            # do nothing
            return

        data = self.cleaned_data

        if not self.user: # meaning add
            education_list = user.educations.all().order_by('pk')[0:4]
        else: # meaning edit
            education_list = self.user.educations.all().order_by('pk')[0:4]

        cnt = 0
        if education_list:
            for i, education in enumerate(education_list):
                cnt = i + 1
                school = data.get('school%s' % cnt, '')
                major = data.get('major%s' % cnt, '')
                degree = data.get('degree%s' % cnt, '')
                graduation_year = data.get('graduation_dt%s' % cnt, 0)
                try:
                    graduation_year = int(graduation_year)
                except ValueError:
                    graduation_year = 0
                education.school=school
                education.major=major
                education.degree=degree
                education.graduation_year=graduation_year
                education.save()

        if cnt < 4:
            for i in range(cnt+1, 5):
                school = data.get('school%s' % i, '')
                major = data.get('major%s' % i, '')
                degree = data.get('degree%s' % i, '')
                graduation_year = data.get('graduation_dt%s' % i, 0)
                try:
                    graduation_year = int(graduation_year)
                except ValueError:
                    graduation_year = 0
                if any([school, major, degree, graduation_year]):
                    Education.objects.create(
                        user=user,
                        school=school,
                        major=major,
                        degree=degree,
                        graduation_year=graduation_year
                    )


class DemographicsForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = MembershipDemographic
        fields = "__all__"

    def __init__(self, app_field_objs, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.membership = kwargs.pop('membership', None)
        super(DemographicsForm, self).__init__(*args, **kwargs)
        assign_fields(self, app_field_objs)
        self.field_names = [name for name in self.fields]
        self.file_upload_fields = {}
        # change the default widget to TextInput instead of TextArea
        for key, field in self.fields.items():
            if field.widget.__class__.__name__.lower() == 'textarea':
                field.widget = forms.widgets.TextInput({'size': 30})
            if 'fileinput' in field.widget.__class__.__name__.lower():
                self.file_upload_fields.update({key:field})
            if field.widget.__class__.__name__.lower() == 'selectdatewidget':
                field.widget.years = list(range(1920, THIS_YEAR + 10))

        self.app = None
        self.demographics = None
        if self.membership:
            self.app = self.membership.app
            self.demographics = self.membership.demographics

        if self.app:
            demographic_fields = get_selected_demographic_fields(self.app, forms)
            for field_name, field in demographic_fields:
                # Commenting out the line below because it loses the field widget as the field has already been assigned
                #self.fields[field_name] = field
                # set initial value
                if self.demographics and field_name in self.fields:
                    ud_field = MembershipAppField.objects.get(field_name=field_name,
                        membership_app=self.app, display=True)
                    if ud_field.field_type == u'FileField':
                        self.fields[field_name] = forms.FileField(label=ud_field.label, required=False)
                        file_instance = get_ud_file_instance(self.demographics, field_name)

                        if file_instance:
                            self.fields[field_name].initial = file_instance.file

                    else:
                        self.fields[field_name].initial = getattr(self.demographics, field_name)

        self.add_form_control_class()

    def save(self, commit=True, *args, **kwargs):
        pks ={}
        if self.file_upload_fields:
            for key in self.file_upload_fields:
                new_file = self.cleaned_data.get(key, None)

                if self.request:
                    clear = self.request.POST.get('%s-clear' % key, False)
                else:
                    clear = None

                if clear and not new_file:
                    file_instance = get_ud_file_instance(self.demographics, key)
                    if file_instance:
                        file_instance.delete()
                        data = u''
                        pks.update({ key : data })

                if new_file:
                    file_instance = get_ud_file_instance(self.demographics, key)

                    if file_instance:
                        file_instance.file = new_file
                    else:
                        file_instance = MembershipFile(file=new_file)

                    file_instance.save()
                    data = {
                        'type' : u'file',
                        'pk' : str(file_instance.pk),
                        'html' : '<a href="%s" target="blank">View here</a>' % file_instance.get_absolute_url(),
                    }
                    data = str(data)
                    pks.update({ key : data })

        demographic = super(DemographicsForm, self).save(commit=commit, *args, **kwargs)
        if pks:
            for key, data in pks.items():
                setattr(demographic, key, data)

        if commit:
            demographic.save()

        return demographic


class MembershipDefault2Form(FormControlWidgetMixin, forms.ModelForm):
    STATUS_DETAIL_CHOICES = (
            ('active', _('Active')),
            ('pending', _('Pending')),
            ('admin_hold', _('Admin Hold')),
            ('inactive', _('Inactive')),
            ('expired', _('Expired')),
            ('archive', _('Archive')),
    )

    STATUS_CHOICES = (
        (1, _('Active')),
        (0, _('Inactive'))
    )

    discount_code = forms.CharField(label=_('Discount Code'), required=False)
#     donation_opt = forms.MultiValueField(required=False)
    payment_method = PaymentMethodModelChoiceField(
        label=_('Payment Method'),
        widget=forms.RadioSelect(),
        empty_label=None,
        queryset=None
    )
    membership_type = MembershipTypeModelChoiceField(
        label=_('Membership Type'),
        empty_label=None,
        queryset=None
    )

    class Meta:
        model = MembershipDefault
        fields = "__all__"

    def __init__(self, app_field_objs, *args, **kwargs):
        request_user = kwargs.pop('request_user')
        customer = kwargs.pop('customer', request_user)
        self.membership_app = kwargs.pop('membership_app')
        multiple_membership = kwargs.pop('multiple_membership', False)
        self.is_renewal = kwargs.pop('is_renewal', False)
        self.renew_from_id = kwargs.pop('renew_from_id', None)
        self.edit_mode = kwargs.pop('edit_mode', False)

        if 'join_under_corporate' in kwargs:
            self.join_under_corporate = kwargs.pop('join_under_corporate')
        else:
            self.join_under_corporate = False
        if 'corp_membership' in kwargs:
            self.corp_membership = kwargs.pop('corp_membership')
        else:
            self.corp_membership = None
        if 'authentication_method' in kwargs:
            self.corp_app_authentication_method = kwargs.pop('authentication_method')
        else:
            self.corp_app_authentication_method = ''

        super(MembershipDefault2Form, self).__init__(*args, **kwargs)

        # NOTE: customer attr is needed by MembershipTypeModelChoiceField!
        self.fields['membership_type'].customer = customer
        if self.corp_membership:
            self.fields['membership_type'].corp_membership = self.corp_membership

        mt_choices = get_membership_type_choices(
            request_user,
            customer,
            self.membership_app,
            corp_membership=self.corp_membership
        )
        mt_choices_pks = [mt_choice[0] for mt_choice in mt_choices]
        mt_choices = MembershipType.objects.filter(pk__in=mt_choices_pks).order_by('position')
        if not self.is_renewal:
            mt_choices = mt_choices.exclude(renewal=True)

        self.fields['membership_type'].queryset = mt_choices

        if multiple_membership:
            self.fields['membership_type'].widget = forms.widgets.CheckboxSelectMultiple(
                choices=self.fields['membership_type'].choices,
            )
        else:
            self.fields['membership_type'].widget = forms.widgets.RadioSelect(
                choices=self.fields['membership_type'].choices,
            )

        if self.corp_membership:
            memb_type = self.corp_membership.corporate_membership_type.membership_type
            self.fields['membership_type'].initial = memb_type
            apply_above_cap, above_cap_price = self.corp_membership.get_above_cap_price()
            if apply_above_cap:
                require_payment =  above_cap_price > 0
            else:
                require_payment = (memb_type.price > 0 or (memb_type.admin_fee and memb_type.admin_fee > 0))
        else:
            # if all membership types are free, no need to display payment method
            require_payment = self.membership_app.membership_types.filter(
                                    Q(price__gt=0) | Q(admin_fee__gt=0)).exists()

        if 'status_detail' in self.fields:
            self.fields['status_detail'].widget = forms.widgets.Select(
                        choices=self.STATUS_DETAIL_CHOICES)
        if 'status' in self.fields:
            self.fields['status'].widget = forms.widgets.Select(
                        choices=self.STATUS_CHOICES)
        if 'groups' in self.fields:
            self.fields['groups'].widget = forms.widgets.CheckboxSelectMultiple()
            self.fields['groups'].queryset = Group.objects.filter(
                                                allow_self_add=True,
                                                show_for_memberships=True,
                                                status=True,
                                                status_detail='active')
            self.fields['groups'].help_text = ''

        if 'corporate_membership_id' in self.fields:
            if self.join_under_corporate and self.corp_membership:
                self.fields['corporate_membership_id'].widget = forms.widgets.Select(
                                        choices=((self.corp_membership.id, self.corp_membership),))
            else:
                self.fields['corporate_membership_id'].widget = forms.widgets.Select(
                                        choices=get_corporate_membership_choices())
                self.fields['corporate_membership_id'].queryset = CorpMembership.objects.filter(
                                                status=True).exclude(
                                                status_detail__in=['archive', 'inactive'])

        assign_fields(self, app_field_objs)
        self.field_names = [name for name in self.fields]

        if self.instance and self.instance.pk:
            self.fields['membership_type'].widget.attrs['disabled'] = 'disabled'
            del self.fields['discount_code']

        if 'renew_dt' in self.fields:
            if not (self.instance and self.instance.renew_dt):
                del self.fields['renew_dt']
            else:
                self.fields['renew_dt'].widget = forms.TextInput(attrs={'readonly': 'readonly'})
                #self.fields['renew_dt'].widget.attrs['readonly'] = 'readonly'

        if not self.edit_mode and self.membership_app.donation_enabled:
            self.fields['donation_option_value'] = DonationOptionAmountField(required=False)
            self.fields['donation_option_value'].label = self.membership_app.donation_label
            self.fields['donation_option_value'].widget = DonationOptionAmountWidget(attrs={},
                                                default_amount=self.membership_app.donation_default_amount)
            require_payment = True

        if self.edit_mode:
            require_payment = False

        if not require_payment:
            if 'payment_method' in self.fields:
                del self.fields['payment_method']
        else:
            payment_method_qs = self.membership_app.payment_methods.all()
            if not (request_user and request_user.is_authenticated and request_user.is_superuser):
                payment_method_qs = payment_method_qs.exclude(admin_only=True)
            self.fields['payment_method'].queryset = payment_method_qs
            if payment_method_qs.count() == 1:
                self.fields['payment_method'].initial = payment_method_qs[0]

        # auto renew field
        if require_payment and payment_method_qs.filter(is_online=True).count() > 0:
            if get_setting('module', 'recurring_payments', 'enabled') and get_setting('module', 'memberships', 'autorenew'):
                if 'corporate_membership_id' not in self.fields:
                    self.fields['auto_renew'] = forms.BooleanField(label=_('Allow Auto Renew (only if credit card payment is selected)'), required=False)
                    self.fields['auto_renew'].initial = True
                    auto_renew_discount = get_setting('module', 'memberships', 'autorenewdiscount')
                    if auto_renew_discount:
                        self.fields['auto_renew'].help_text = _('A {} discount will be applied immediately if you opt in Auto Renew').format(
                                                                    tcurrency(auto_renew_discount))

        self.add_form_control_class()

    def clean_donation_option_value(self):
        value_list = self.cleaned_data['donation_option_value']
        if value_list:
            donation_option, donation_amount = value_list
            if donation_option == 'custom':
                # validate donation_amount
                try:
                    donation_amount = donation_amount.replace('$', '').replace(',', '')
                    donation_amount = decimal.Decimal(donation_amount)
                    return (donation_option, donation_amount)
                except decimal.InvalidOperation:
                    raise forms.ValidationError(_("Please enter a valid donation amount."))

        return value_list

    def clean_auto_renew(self):
        value = self.cleaned_data['auto_renew']
        if value:
            payment_method = self.cleaned_data.get('payment_method')
            if not payment_method or not payment_method.is_online:
                raise forms.ValidationError(_("Please either de-select it or change to an online payment method."))
        return value

    def save(self, *args, **kwargs):
        """
        Create membership record.
        Handle all objects:
            Membership
            Membership.user
            Membership.user.profile
            Membership.invoice
            Membership.user.group_set()
        """
        user = kwargs.pop('user')
        request = kwargs.pop('request')

        request_user = None
        if hasattr(request, 'user'):
            if isinstance(request.user, User):
                request_user = request.user

        kwargs['commit'] = False
        membership = super(MembershipDefault2Form, self).save(*args, **kwargs)

#         is_renewal = False
#         if request_user:
#             m_list = MembershipDefault.objects.filter(
#                 user=request_user, membership_type=membership.membership_type
#             )
#             is_renewal = any([m.can_renew() for m in m_list])

        # assign corp_profile_id
        if membership.corporate_membership_id:
            corp_membership = CorpMembership.objects.get(
                pk=membership.corporate_membership_id
            )
            membership.corp_profile_id = corp_membership.corp_profile.id
            membership.entity = corp_membership.corp_profile.entity

        # set owner & creator
        if request_user:
            if not self.edit_mode:
                membership.creator = request_user
                membership.creator_username = request_user.username
            membership.owner = request_user
            membership.owner_username = request_user.username

        if 'membership-referer-url' in request.session:
            membership.referer_url = request.session['membership-referer-url']

        if not membership.entity:
            membership.entity = Entity.objects.first()
        membership.user = user

        # adding membership record
        membership.renewal = self.is_renewal
        if self.renew_from_id:
            membership.renew_from_id = self.renew_from_id

        # set app
        membership.app = self.membership_app

        # create record in database
        # helps with associating invoice record
        membership.save()
        # save many-to-many data for the form
        self.save_m2m()

        # assign member number
        membership.set_member_number()
        membership.save()

        return membership


class MembershipExportForm(forms.Form):

    STATUS_DETAIL_CHOICES = (
        ('active', _('Export Active Memberships')),
        ('pending', _('Export Pending Memberships')),
        ('expired', _('Export Expired Memberships')),
    )

    EXPORT_FIELD_CHOICES = (
        ('main_fields', _('Export Main Fields (fastest)')),
        ('all_fields', _('Export All Fields')),
    )

    export_format = forms.CharField(widget=forms.HiddenInput(), initial='csv')
    export_status_detail = forms.ChoiceField(choices=STATUS_DETAIL_CHOICES)
    export_fields = forms.ChoiceField(choices=EXPORT_FIELD_CHOICES)
    export_type = forms.ChoiceField(choices=())

    def __init__(self, *args, **kwargs):
        super(MembershipExportForm, self).__init__(*args, **kwargs)
        EXPORT_TYPE_CHOICES = [(u'all', _('Export All Types'))] + \
                list(MembershipType.objects.values_list('pk', 'name'))
        self.fields['export_type'].choices = EXPORT_TYPE_CHOICES


class NoticeForm(forms.ModelForm):
    notice_time_type = NoticeTimeTypeField(label=_('When to Send'),
                                          widget=NoticeTimeTypeWidget)
    email_content = forms.CharField(widget=TinyMCE(attrs={'style': 'width:70%'},
        mce_attrs={'storme_app_label': Notice._meta.app_label,
        'storme_model': Notice._meta.model_name.lower()}), help_text=_("Click here to view available tokens"))

    class Meta:
        model = Notice
        fields = (
                  'notice_name',
                  'notice_time_type',
                  'membership_type',
                  'subject',
                  'content_type',
                  'sender',
                  'sender_display',
                  'email_content',
                  'status',
                  'status_detail',
                  )

    def __init__(self, *args, **kwargs):
        super(NoticeForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['email_content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['email_content'].widget.mce_attrs['app_instance_id'] = 0

        initial_list = []
        if self.instance.pk:
            initial_list.append(str(self.instance.num_days))
            initial_list.append(str(self.instance.notice_time))
            initial_list.append(str(self.instance.notice_type))

        self.fields['notice_time_type'].initial = initial_list

        self.fields['email_content'].help_text = get_notice_token_help_text(self.instance)

    def clean_notice_time_type(self):
        value = self.cleaned_data['notice_time_type']

        data_list = value.split(',')
        d = dict(zip(['num_days', 'notice_time', 'notice_type'], data_list))

        try:
            d['num_days'] = int(d['num_days'])
        except:
            raise forms.ValidationError(_("Num days must be a numeric number."))
        return value


class AppCorpPreForm(FormControlWidgetMixin, forms.Form):
    corporate_membership_id = forms.ChoiceField(
                            label=_('Join Under the Corporation:'))
    secret_code = forms.CharField(
                        label=_('Enter the Secret Code'),
                        max_length=50)
    email = EmailVerificationField(
                    label=_('Verify Your Email Address'),
                    help_text=_("""Your email address will be used to locate your corporate account.
                    Please click the link in the verification email received to continue your application.
                    Thanks!"""))

    def __init__(self, *args, **kwargs):
        super(AppCorpPreForm, self).__init__(*args, **kwargs)
        self.auth_method = ''
        self.corporate_membership_id = 0

    def clean_secret_code(self):
        secret_code = self.cleaned_data['secret_code']
        [corp_membership] = CorpMembership.objects.filter(
                                   corp_profile__secret_code=secret_code,
                                   status=True,
                                   status_detail='active')[:1] or [None]
        if not corp_membership:
            raise forms.ValidationError(_("Invalid Secret Code."))

        self.corporate_membership_id = corp_membership.id
        return secret_code

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            email_domain = (email.split('@')[1]).strip()
            auth_domains = CorpMembershipAuthDomain.objects.filter(
                                    name=email_domain).filter(
                                    corp_profile__status_detail='active')
            corp_membership = None
            # check which corp. membership carries this auth domain
            if auth_domains:
                for auth_domain in auth_domains:
                    corp_membership = auth_domain.corp_profile.active_corp_membership
                    if corp_membership:
                        break

            if not corp_membership:
                raise forms.ValidationError(
                    _("Sorry but we're not able to find your corporation."))
            self.corporate_membership_id = corp_membership.id
        return email


class ReportForm(forms.Form):
    STATUS_CHOICES = (
        ('', _('All Statuses')),
        ('active', _('Active')),
        ('expired', _('Expired')),
    )

    start_date = forms.DateField(
        widget=forms.TextInput(
            attrs={'class': 'input-small', 'placeholder': 'Start Date'}))

    end_date = forms.DateField(
        widget=forms.TextInput(
            attrs={'class': 'input-small', 'placeholder': 'End Date'}))

    membership_type = forms.ModelChoiceField(
        queryset=MembershipType.objects.all(),
        empty_label='All Types',
        required=False)

    membership_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False)


class MembershipDefaultForm(TendenciBaseForm):
    """
    Bound to the MembershipDefault model
    """

    salutation = forms.CharField(required=False)
    first_name = forms.CharField(initial=u'')
    last_name = forms.CharField(initial=u'')
    email = forms.CharField(initial=u'')
    email2 = forms.CharField(initial=u'', required=False)
    display_name = forms.CharField(initial=u'', required=False)
    company = forms.CharField(initial=u'', required=False)
    position_title = forms.CharField(initial=u'', required=False)
    education = forms.CharField(label=_('Highest Level of Education'), initial=u'', required=False)
    department = forms.CharField(initial=u'', required=False)
    address = forms.CharField(initial=u'', required=False)
    address2 = forms.CharField(initial=u'', required=False)
    address_type = forms.CharField(initial=u'', required=False)
    city = forms.CharField(initial=u'', required=False)
    state = forms.CharField(initial=u'', required=False)
    zipcode = forms.CharField(initial=u'', required=False)
    country = CountrySelectField(label=_('Country'), required=False)
    phone = forms.CharField(initial=u'', required=False)
    phone2 = forms.CharField(initial=u'', required=False)
    work_phone = forms.CharField(initial=u'', required=False)
    home_phone = forms.CharField(initial=u'', required=False)
    mobile_phone = forms.CharField(initial=u'', required=False)
    pager = forms.CharField(initial=u'', required=False)
    fax = forms.CharField(initial=u'', required=False)
    url = forms.CharField(initial=u'', required=False)
    url2 = forms.CharField(initial=u'', required=False)

    hide_in_search = forms.BooleanField(required=False)
    hide_address = forms.BooleanField(required=False)
    hide_email = forms.BooleanField(required=False)
    hide_phone = forms.BooleanField(required=False)

    # alternate address goes here
    address_2 = forms.CharField(initial=u'', required=False, max_length=64)
    address2_2 = forms.CharField(initial=u'', required=False, max_length=64)
    city_2 = forms.CharField(initial=u'', required=False, max_length=35)
    state_2 = forms.CharField(initial=u'', required=False, max_length=35)
    zipcode_2 = forms.CharField(initial=u'', required=False, max_length=16)
    country_2 = CountrySelectField(label=_('Country'), required=False)

    dob = forms.DateTimeField(required=False)
    education_grad_dt = forms.DateTimeField(required=False)
    career_start_dt = forms.DateTimeField(required=False)
    career_end_dt = forms.DateTimeField(required=False)

    sex = forms.CharField(label=_('Gender'), initial=u'', required=False)
    spouse = forms.CharField(initial=u'', required=False)
    profession = forms.CharField(initial=u'', required=False)
    custom1 = forms.CharField(initial=u'', required=False)
    custom2 = forms.CharField(initial=u'', required=False)
    custom3 = forms.CharField(initial=u'', required=False)
    custom4 = forms.CharField(initial=u'', required=False)

    username = forms.CharField(initial=u'', required=False)
    password = forms.CharField(initial=u'', widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(initial=u'', widget=forms.PasswordInput, required=False)

    same_as_primary = forms.BooleanField(required=False)
    extra_address = forms.CharField(initial=u'', required=False)
    extra_address2 = forms.CharField(initial=u'', required=False)
    extra_city = forms.CharField(initial=u'', required=False)
    extra_state = forms.CharField(initial=u'', required=False)
    extra_zip_code = forms.CharField(initial=u'', required=False)
    extra_country = forms.CharField(initial=u'', required=False)
    extra_address_type = forms.CharField(initial=u'', required=False)

    #education fields here
    school1 = forms.CharField(initial=u'', required=False)
    major1 = forms.CharField(initial=u'', required=False)
    degree1 = forms.CharField(initial=u'', required=False)
    graduation_dt1 = forms.ChoiceField(label=_('Graduation Year1'),
                                       required=False, choices=YEAR_CHOICES)
    school2 = forms.CharField(initial=u'', required=False)
    major2 = forms.CharField(initial=u'', required=False)
    degree2 = forms.CharField(initial=u'', required=False)
    graduation_dt2 = forms.ChoiceField(label=_('Graduation Year2'),
                                       required=False, choices=YEAR_CHOICES)
    school3 = forms.CharField(initial=u'', required=False)
    major3 = forms.CharField(initial=u'', required=False)
    degree3 = forms.CharField(initial=u'', required=False)
    graduation_dt3 = forms.ChoiceField(label=_('Graduation Year3'),
                                       required=False, choices=YEAR_CHOICES)
    school4 = forms.CharField(initial=u'', required=False)
    major4 = forms.CharField(initial=u'', required=False)
    degree4 = forms.CharField(initial=u'', required=False)
    graduation_dt4 = forms.ChoiceField(label=_('Graduation Year4'),
                                       required=False, choices=YEAR_CHOICES)

    # manually add ud fields here because admin.site.register requires it
    ud1 = forms.CharField(widget=forms.TextInput, required=False)
    ud2 = forms.CharField(widget=forms.TextInput, required=False)
    ud3 = forms.CharField(widget=forms.TextInput, required=False)
    ud4 = forms.CharField(widget=forms.TextInput, required=False)
    ud5 = forms.CharField(widget=forms.TextInput, required=False)
    ud6 = forms.CharField(widget=forms.TextInput, required=False)
    ud7 = forms.CharField(widget=forms.TextInput, required=False)
    ud8 = forms.CharField(widget=forms.TextInput, required=False)
    ud9 = forms.CharField(widget=forms.TextInput, required=False)
    ud10 = forms.CharField(widget=forms.TextInput, required=False)
    ud11 = forms.CharField(widget=forms.TextInput, required=False)
    ud12 = forms.CharField(widget=forms.TextInput, required=False)
    ud13 = forms.CharField(widget=forms.TextInput, required=False)
    ud14 = forms.CharField(widget=forms.TextInput, required=False)
    ud15 = forms.CharField(widget=forms.TextInput, required=False)
    ud16 = forms.CharField(widget=forms.TextInput, required=False)
    ud17 = forms.CharField(widget=forms.TextInput, required=False)
    ud18 = forms.CharField(widget=forms.TextInput, required=False)
    ud19 = forms.CharField(widget=forms.TextInput, required=False)
    ud20 = forms.CharField(widget=forms.TextInput, required=False)
    ud21 = forms.CharField(widget=forms.TextInput, required=False)
    ud22 = forms.CharField(widget=forms.TextInput, required=False)
    ud23 = forms.CharField(widget=forms.TextInput, required=False)
    ud24 = forms.CharField(widget=forms.TextInput, required=False)
    ud25 = forms.CharField(widget=forms.TextInput, required=False)
    ud26 = forms.CharField(widget=forms.TextInput, required=False)
    ud27 = forms.CharField(widget=forms.TextInput, required=False)
    ud28 = forms.CharField(widget=forms.TextInput, required=False)
    ud29 = forms.CharField(widget=forms.TextInput, required=False)
    ud30 = forms.CharField(widget=forms.TextInput, required=False)

    class Meta:
        model = MembershipDefault
        fields = (
            'member_number',
            'membership_type',
            'renewal',
            'certifications',
            'work_experience',
            'referral_source',
            'referral_source_other',
            'referral_source_member_name',
            'referral_source_member_number',
            'affiliation_member_number',
            'primary_practice',
            'how_long_in_practice',
            'notes',
            'admin_notes',
            'newsletter_type',
            'directory_type',
            'application_approved',
            'payment_method',
            'chapter',
            'areas_of_expertise',
            'corporate_membership_id',
            'home_state',
            'year_left_native_country',
            'network_sectors',
            'networking',
            'government_worker',
            'government_agency',
            'license_number',
            'license_state',
            'region',
            'industry',
            'company_size',
            'promotion_code',
            'directory',
            'join_dt',
            'renew_dt',
            'expire_dt',
        )
        widgets = {
            'membership_type': forms.RadioSelect,
            'payment_method': forms.RadioSelect,
            'bod_dt': forms.DateTimeInput(attrs={'class': 'datepicker'}),
            'application_approved_denied_dt': forms.DateTimeInput(
                attrs={'class': 'datepicker'}),
            'application_complete_dt': forms.DateTimeInput(
                attrs={'class': 'datepicker'}),
            'action_taken_dt': forms.DateTimeInput(
                attrs={'class': 'datepicker'}),
            'personnel_notified_dt': forms.DateTimeInput(
                attrs={'class': 'datepicker'}),
            'payment_received_dt': forms.DateTimeInput(
                attrs={'class': 'datepicker'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Setting foreign key fields with temporary objects.
        """
        request = kwargs.pop('request', None)

        request_user = None
        if hasattr(request, 'user'):
            if isinstance(request.user, User):
                request_user = request.user

        super(MembershipDefaultForm, self).__init__(*args, **kwargs)

        # initialize field widgets ---------------------------
        self.fields['payment_method'].empty_label = None
        # make payment_method not required for admin - this form is used only at admin backend
        self.fields['payment_method'].required = False
        self.fields['industry'].empty_label = 'Select One'
        self.fields['region'].empty_label = 'Select One'

        if not self.instance.pk:
            self.fields['dob'].widget = forms.DateTimeInput(attrs={'class': 'datepicker'})
            self.fields['education_grad_dt'].widget = forms.DateTimeInput(attrs={'class': 'datepicker'})
            self.fields['career_start_dt'].widget = forms.DateTimeInput(attrs={'class': 'datepicker'})
            self.fields['career_end_dt'].widget = forms.DateTimeInput(attrs={'class': 'datepicker'})

        self.fields['corporate_membership_id'].widget = forms.widgets.Select(
                                        choices=get_corporate_membership_choices(active_only=False))
        self.fields['corporate_membership_id'].queryset = CorpMembership.objects.filter(
                                        status=True).exclude(
                                        status_detail__in=['archive', 'inactive'])

        mts = MembershipType.objects.filter(status=True, status_detail='active')
        mt_values = mts.values_list('pk', 'name', 'price', 'renewal_price', 'admin_fee')

        renew_mode = False
        if hasattr(request_user, 'profile'):
            renew_mode = request_user.profile.can_renew()

        # only include admin fee on join

        mt_choices = []
        for pk, name, price, renewal_price, admin_fee in mt_values:
            price = price or float()
            renewal_price = renewal_price or float()
            admin_fee = admin_fee or float()

            if renew_mode:
                mt_choices.append((pk, '%s $%s' % (name, renewal_price)))
            else:
                if admin_fee:
                    mt_choices.append((pk, '%s $%s ($%s admin fee)' % (name, price, admin_fee)))
                else:
                    mt_choices.append((pk, '%s $%s' % (name, price)))

        self.fields['membership_type'].choices = mt_choices
        # -----------------------------------------------------

        # change form -----------------------------------------
        if self.instance.pk:

            user_attrs = [
                'first_name',
                'last_name',
                'email',
            ]

            profile_attrs = [
                'email2',
                'company',
                'department',
                'position_title',
                'education',
                'address',
                'address2',
                'address_type',
                'city',
                'state',
                'zipcode',
                'country',
                'phone',
                'phone2',
                'work_phone',
                'home_phone',
                'mobile_phone',
                'fax',
                'url',
                'url2',
                'dob',
                'sex',
                'spouse',
                'hide_in_search',
                'hide_address',
                'hide_email',
                'hide_phone',
                # alternate address fields here
                'address_2',
                'address2_2',
                'city_2',
                'state_2',
                'zipcode_2',
                'country_2',
            ]

            # initialize user fields
            for user_attr in user_attrs:
                self.fields[user_attr].initial = \
                    getattr(self.instance.user, user_attr)

            # initialize profile fields
            if hasattr(self.instance.user, 'profile'):
                for profile_attr in profile_attrs:
                    self.fields[profile_attr].initial = \
                        getattr(self.instance.user.profile, profile_attr)
            else:
                Profile.objects.create_profile(user=self.instance.user)

            if 'renew_dt' in self.fields:
                self.fields['renew_dt'].widget.attrs['readonly'] = 'readonly'
        # -----------------------------------------------------

            # initialize education fields
            self.education_list = self.instance.user.educations.all().order_by('pk')[0:4]
            cnt = 1
            if self.education_list:
                for education in self.education_list:
                    self.fields['school%s' % cnt].initial = education.school
                    self.fields['major%s' % cnt].initial = education.major
                    self.fields['degree%s' % cnt].initial = education.degree
                    self.fields['graduation_dt%s' % cnt].initial = education.graduation_year
                    cnt += 1

        # demographic fields - include only those selected on app
        demographic_field_names = [field.name
                        for field in MembershipDemographic._meta.fields
                        if field.get_internal_type() != 'AutoField']
        for field_name in demographic_field_names:
            if hasattr(self.fields, field_name):
                del self.fields[field_name]

        demographics = self.instance.demographics

        if self.instance and self.instance.app:
            app = self.instance.app
        else:
            app = MembershipApp.objects.current_app()

        self._app = app
        demographic_fields = get_selected_demographic_fields(app, forms)
        self.demographic_field_names = [field_item[0] for field_item in demographic_fields]
        for field_name, field in demographic_fields:
            self.fields[field_name] = field
            # set initial value
            if demographics:
                ud_field = MembershipAppField.objects.get(field_name=field_name,
                    membership_app=app, display=True)
                if ud_field.field_type == u'FileField':
                    self.fields[field_name] = forms.FileField(label=ud_field.label, required=False)
                    file_instance = get_ud_file_instance(demographics, field_name)

                    if file_instance:
                        self.fields[field_name].initial = file_instance.file

                else:
                    self.fields[field_name].initial = getattr(demographics, field_name)
        # end demographic

        # industry field
        [industry_field] = MembershipAppField.objects.filter(field_name='industry',
                    membership_app=app, display=True)[:1] or [None]
        if industry_field:
            self.fields['industry'].label = industry_field.label

    def clean(self):
        """
        Validating username and password fields.
        """
        super(MembershipDefaultForm, self).clean()

        data = self.cleaned_data

        un = data.get('username', u'').strip()
        pw = data.get('password', u'').strip()
        pw_confirm = data.get('confirm_password', u'').strip()

        if un and pw:
            # assert passwords match
            if pw != pw_confirm:
                raise forms.ValidationError(
                    _('Passwords do not match.')
                )

            [u] = User.objects.filter(username=un)[:1] or [None]

            if u:
                # assert password;
                if not u.check_password(pw):
                    raise forms.ValidationError(
                        _('Username and password did not match.')
                    )
            else:
                pass
                # username does not exist;
                # create account with username and password

        elif un:
            [u] = User.objects.filter(username=un)[:1] or [None]
            # assert username
            if u:
                raise forms.ValidationError(
                    _('This username exists. If it\'s yours, please provide your password.')
                )

        return data

    def save(self, *args, **kwargs):
        """
        Create membership record.
        Handle all objects:
            Membership
            Membership.user
            Membership.user.profile
            Membership.user.education
            Membership.invoice
            Membership.user.group_set()
        """
        request = kwargs.pop('request')

        request_user = None
        if hasattr(request, 'user'):
            if isinstance(request.user, User):
                request_user = request.user

        membership = super(MembershipDefaultForm, self).save(*args, **kwargs)

        if request_user:
            membership.creator = request_user
            membership.creator_username = request_user.username
            membership.owner = request_user
            membership.owner_username = request_user.username

        membership.entity = Entity.objects.first()

        # get or create user
        membership.user, created = membership.get_or_create_user(**{
            'username': self.cleaned_data.get('username'),
            'password': self.cleaned_data.get('password'),
            'first_name': self.cleaned_data.get('first_name'),
            'last_name': self.cleaned_data.get('last_name'),
            'email': self.cleaned_data.get('email')
        })

        # assign corp_profile_id
        if membership.corporate_membership_id:
            corp_membership = CorpMembership.objects.get(
                pk=membership.corporate_membership_id
            )
            membership.corp_profile_id = corp_membership.corp_profile.id

        if membership.pk:
            # changing membership record
            membership.set_member_number()
            membership.user.profile.member_number = membership.member_number
            membership.user.profile.save()
        else:
            # adding membership record
            membership.renewal = membership.user.profile.can_renew()

            # create record in database
            # helps with associating invoice record
            membership.save()

            NOW = datetime.now()

            if not membership.approval_required():  # approval not required

                # save invoice tendered
                membership.save_invoice(status_detail='tendered')

                # auto approve -------------------------
                membership.application_approved = True
                membership.application_approved_user = \
                    request_user or membership.user
                membership.application_approved_dt = NOW

                membership.application_approved_denied_user = \
                    request_user or membership.user

                membership.set_join_dt()
                membership.set_renew_dt()
                membership.set_expire_dt()

                membership.archive_old_memberships()
                membership.send_email(request, ('approve_renewal' if membership.is_renewal() else 'approve'))

            else:  # approval required
                # save invoice estimate
                membership.save_invoice(status_detail='estimate')

            # application complete
            membership.application_complete_dt = NOW
            membership.application_complete_user = membership.user

            # save application fields
            # save join, renew, and expire dt
            membership.save()

            # save education fields ----------------------------
        if self.education_list: # meaning education instances exists already
            cnt = 1
            for education in self.education_list:
                school = request.POST.get('school%s' % cnt, '')
                major = request.POST.get('major%s' % cnt, '')
                degree = request.POST.get('degree%s' %cnt, '')
                graduation_year = request.POST.get('graduation_dt%s' % cnt, 0)
                try:
                    graduation_year = int(graduation_year)
                except ValueError:
                    graduation_year = 0
                if any([school, major, degree, graduation_year]):
                    education.school=school
                    education.major=major
                    education.degree=degree
                    education.graduation_year=graduation_year
                    education.save()

                cnt += 1

            current_count = cnt
            if current_count < 4: # not all education fields have entries before
                for cnt in range(current_count, 5):
                    school = request.POST.get('school%s' % cnt, '')
                    major = request.POST.get('major%s' % cnt, '')
                    degree = request.POST.get('degree%s' %cnt, '')
                    graduation_year = request.POST.get('graduation_dt%s' % cnt, 0)
                    try:
                        graduation_year = int(graduation_year)
                    except ValueError:
                        graduation_year = 0
                    if any([school, major, degree, graduation_year]):
                        Education.objects.create(
                            user=membership.user,
                            school=school,
                            major=major,
                            degree=degree,
                            graduation_year=graduation_year
                        )

        else:   # create education instances here
            for cnt in range(1,5):
                school = request.POST.get('school%s' % cnt, '')
                major = request.POST.get('major%s' % cnt, '')
                degree = request.POST.get('degree%s' %cnt, '')
                graduation_year = request.POST.get('graduation_dt%s' % cnt, 0)
                try:
                    graduation_year = int(graduation_year)
                except ValueError:
                    graduation_year = 0
                if any([school, major, degree, graduation_year]):
                    Education.objects.create(
                        user=membership.user,
                        school=school,
                        major=major,
                        degree=degree,
                        graduation_year=graduation_year
                    )

            # save career fields -------------------------------
            careers = zip(
                request.POST.getlist('career_name'),
                request.POST.getlist('career_description'),
                request.POST.getlist('position_title'),
                request.POST.getlist('position_description'),
                request.POST.getlist('career_start_dt'),
                request.POST.getlist('career_end_dt'),
            )

            for career in careers:
                if any(career) and all(career[4:]):
                    (career_name, career_description, position_title,
                        position_description, career_start_dt, career_end_dt) = career
                    Career.objects.create(
                        company=career_name,
                        company_description=career_description,
                        position_title=position_title,
                        position_description=position_description,
                        start_dt=career_start_dt,
                        end_dt=career_end_dt,
                    )
            # --------------------------------------------------

            # send welcome email; if required
            if created:
                send_welcome_email(membership.user)

        # [un]subscribe to group
        membership.group_refresh()

        if membership.application_approved:
            membership.archive_old_memberships()
            membership.save_invoice(status_detail='tendered')

        # loop through & set these user attributes
        # user.first_name = self.cleaned_data.get('first_name', u'')
        user_attrs = [
            'first_name',
            'last_name',
            'email',
        ]

        for i in user_attrs:
            setattr(membership.user, i, self.cleaned_data.get(i, u''))
        membership.user.save()
        # -----------------------------------------------------------

        # loop through & set these profile attributes
        # profile.display_name = self.cleaned_data.get('display_name', u'')
        profile_attrs = [
            'display_name',
            'company',
            'position_title',
            'education',
            # 'functional_title',
            'department',
            'address',
            'address2',
            'city',
            'state',
            'zipcode',
            'country',
            'address_type',
            'phone',
            'phone2',
            'work_phone',
            'home_phone',
            'mobile_phone',
            # 'pager',
            'fax',
            'email',
            'email2',
            'url',
            'url2',
            'hide_in_search',
            'hide_address',
            'hide_email',
            'hide_phone',
            'dob',
            'sex',
            'spouse',
            # alternate address fields here
            'address_2',
            'address2_2',
            'city_2',
            'state_2',
            'zipcode_2',
            'country_2',
        ]

        for i in profile_attrs:
            setattr(membership.user.profile, i, self.cleaned_data.get(i, u''))
        membership.user.profile.save()
        # -----------------------------------------------------------------

        # ***** demographics *****

        if self.demographic_field_names:
            demographics, created = MembershipDemographic.objects.get_or_create(
                                            user=membership.user)

            for field_name in self.demographic_field_names:
                ud_field = MembershipAppField.objects.get(field_name=field_name,
                     membership_app=self._app, display=True)
                if ud_field.field_type == u'FileField':
                    # get the file instance
                    new_file = self.cleaned_data.get(field_name, None)
                    # check if cleared:
                    clear = request.POST.get('%s-clear' % field_name, False)
                    if clear and not new_file:
                        file_instance = get_ud_file_instance(demographics, field_name)

                        if file_instance:
                            file_instance.delete()
                            setattr(demographics, field_name, '')

                    if new_file:
                        file_instance = get_ud_file_instance(demographics, field_name)

                        if file_instance:
                            file_instance.file = new_file
                        else:
                            file_instance = MembershipFile(file=new_file)

                        file_instance.save()
                        data = {
                            'type' : u'file',
                            'pk' : str(file_instance.pk),
                            'html' : '<a href="%s" target="blank">View here</a>' % file_instance.get_absolute_url(),
                        }
                        data = str(data)
                        setattr(demographics, field_name, data)

                else:
                    setattr(demographics, field_name,
                        self.cleaned_data.get(field_name, ''))
            demographics.save()
        # ***** end demographics *****

        return membership
