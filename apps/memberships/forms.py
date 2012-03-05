import sys
from uuid import uuid4
from captcha.fields import CaptchaField
from os.path import join
from datetime import datetime
from hashlib import md5

from django.contrib.auth.models import User, AnonymousUser
from django.forms.fields import CharField, ChoiceField, BooleanField
from django.template.defaultfilters import slugify
from django.forms.widgets import HiddenInput
from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.importlib import import_module
from django.core.files.storage import FileSystemStorage

from haystack.query import SearchQuerySet
from tinymce.widgets import TinyMCE

from perms.utils import is_admin

from corporate_memberships.models import CorporateMembership, AuthorizedDomain
from user_groups.models import Group
from perms.forms import TendenciBaseForm

from memberships.models import MembershipType, Notice, App, AppEntry, AppField, AppFieldEntry
from memberships.fields import TypeExpMethodField, PriceInput, NoticeTimeTypeField
from memberships.settings import FIELD_MAX_LENGTH, UPLOAD_ROOT
from memberships.utils import csv_to_dict, is_import_valid
from memberships.widgets import CustomRadioSelect, TypeExpMethodWidget, NoticeTimeTypeWidget

from memberships.utils import get_notice_token_help_text

fs = FileSystemStorage(location=UPLOAD_ROOT)

type_exp_method_fields = (
    'period_type', 'period', 'period_unit', 'rolling_option',
    'rolling_option1_day', 'rolling_renew_option', 'rolling_renew_option1_day',
    'rolling_renew_option2_day', 'fixed_option','fixed_option1_day',
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
    'date': ('DateField', 'django.forms.extras.SelectDateWidget'),
    'date-time': ('DateTimeField', None),
    'membership-type': ('ChoiceField', 'django.forms.RadioSelect'),
    'payment-method': ('ChoiceField', None),
    'first-name': ('CharField', None),
    'last-name': ('CharField', None),
    'email': ('EmailField', None),
    'header': ('CharField', 'memberships.widgets.Header'),
    'description': ('CharField', 'memberships.widgets.Description'),
    'horizontal-rule': ('CharField', 'memberships.widgets.Description'),
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
        mentioned_fn = entry.first_name
        mentioned_ln = entry.last_name
        mentioned_em = entry.email
    else:
        mentioned_fn, mentioned_ln, mentioned_em = None, None, None

    sqs = SearchQuerySet()

#    full_name_q = Q(content='%s %s' % (mentioned_fn, mentioned_ln))
    email_q = Q(content=mentioned_em)
#    q = reduce(operator.or_, [full_name_q, email_q])
    sqs = sqs.filter(email_q)

    sqs_users = [sq.object.user for sq in sqs]

    for u in sqs_users:
        user_set[u.pk] = '%s %s %s %s' % (u.first_name, u.last_name, u.username, u.email)

    user_set[0] = 'Create new user'

    return user_set.items()


class MemberApproveForm(forms.Form):

    users = forms.ChoiceField(
        label='Connect this membership with',
        choices=[],
        widget=forms.RadioSelect,
        )

    def get_suggestions(self, entry):
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
            mentioned_fn = entry.first_name
            mentioned_ln = entry.last_name
            mentioned_em = entry.email
        else:
            mentioned_fn, mentioned_ln, mentioned_em = None, None, None

        sqs = SearchQuerySet()

        if mentioned_em:
            email_q = Q(content=mentioned_em)
            sqs = sqs.filter(email_q)
            sqs_users = [sq.object.user for sq in sqs]
        else:
            sqs_users = []

        for u in sqs_users:
            user_set[u.pk] = '%s %s %s %s' % (u.first_name, u.last_name, u.username, u.email)
            self.fields['users'].initial = u.pk

        user_set[0] = 'Create new user'

        return user_set.items()

    def __init__(self, entry, *args, **kwargs):
        super(MemberApproveForm, self).__init__(*args, **kwargs)
        suggested_users = []
        self.entry = entry

        suggested_users = entry.suggested_users(grouping=[('email',)])
        suggested_users.append((0, 'Create new user'))
        self.fields['users'].choices = suggested_users
        self.fields['users'].initial = 0

        if self.entry.is_renewal:            
            self.fields['users'] = CharField(
                label='',
                initial=entry.user.pk, 
                widget=HiddenInput
            )


class MembershipTypeForm(forms.ModelForm):
    type_exp_method = TypeExpMethodField(label='Period Type')
    description = forms.CharField(label=_('Notes'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    price = forms.DecimalField(decimal_places=2, widget=PriceInput(), 
                               help_text="Set 0 for free membership.")
    renewal_price = forms.DecimalField(decimal_places=2, widget=PriceInput(), required=False, 
                               help_text="Set 0 for free membership.")
    admin_fee = forms.DecimalField(decimal_places=2, required=False,
                                   widget=PriceInput(),
                                   help_text="Admin fee for the first time processing")
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('admin hold','Admin Hold'),))
    
    class Meta:
        model = MembershipType
        fields = (
                  'app',
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
                  'admin_only',
                  'renewal_require_approval',
                  'renewal_period_start',
                  'renewal_period_end',
                  'expiration_grace_period',
                  'order',
                  'status',
                  'status_detail',
                  )

    def __init__(self, *args, **kwargs): 
        super(MembershipTypeForm, self).__init__(*args, **kwargs)
        
        self.type_exp_method_fields = type_exp_method_fields
        
        initial_list = []
        if self.instance.pk:
            for field in self.type_exp_method_fields:
                field_value = eval('self.instance.%s' % field)
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
        
        self.fields['type_exp_method'].widget = TypeExpMethodWidget(attrs={'id':'type_exp_method'},
                                                                    fields_pos_d=fields_pos_d) 
        
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
        
        else: # d['period_type'] == 'fixed'
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
                
            if d.has_key('fixed_option2_can_rollover') and d['fixed_option2_can_rollover']:
                try:
                    d['fixed_option2_rollover_days'] = int(d['fixed_option2_rollover_days'])
                except:
                    raise forms.ValidationError(_("The grace period day(s) for optoin 2 must be a numeric number."))
        
        return value
    
    def save(self, *args, **kwargs):
        return super(MembershipTypeForm, self).save(*args, **kwargs)
    
    
class NoticeForm(forms.ModelForm):
    notice_time_type = NoticeTimeTypeField(label='When to Send',
                                          widget=NoticeTimeTypeWidget)
    email_content = forms.CharField(widget=TinyMCE(attrs={'style':'width:70%'}, 
        mce_attrs={'storme_app_label':Notice._meta.app_label, 
        'storme_model':Notice._meta.module_name.lower()}), help_text="Click here to view available tokens")    
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
            
    
class AppCorpPreForm(forms.Form):
    corporate_membership_id = forms.ChoiceField(label=_('Join Under the Corporation:'))
    secret_code = forms.CharField(label=_('Enter the Secret Code'), max_length=50)
    email = forms.EmailField(label=_('Verify Your Email Address'), max_length=100,
                             help_text="""Your email address will help us to identify your corporate.
                                         You will receive an email to the address you entered for us
                                         to verify your email address. 
                                         Please follow the instruction
                                         in the email to continue signing up for the membership.
                                          """)
    
    def __init__(self, *args, **kwargs):
        super(AppCorpPreForm, self).__init__(*args, **kwargs)
        self.auth_method = ''
        self.corporate_membership_id = 0
    
    def clean_secret_code(self):
        secret_code = self.cleaned_data['secret_code']
        corporate_memberships = CorporateMembership.objects.filter(secret_code=secret_code, 
                                                                   status=1,
                                                                   status_detail='active')
        if not corporate_memberships:
            raise forms.ValidationError(_("Invalid Secret Code."))
        
        self.corporate_membership_id = corporate_memberships[0].id
        return secret_code
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            email_domain = (email.split('@')[1]).strip()
            auth_domains = AuthorizedDomain.objects.filter(name=email_domain)
            if not auth_domains:
                raise forms.ValidationError(_("Sorry but we're not able to find your corporation."))
            self.corporate_membership_id = auth_domains[0].corporate_membership.id 
        return email 

class AppForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':App._meta.app_label, 
        'storme_model':App._meta.module_name.lower()}))

    confirmation_text = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':App._meta.app_label, 
        'storme_model':App._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(choices=(('draft','Draft'),('published','Published')))

    class Meta:
        model = App

    def __init__(self, *args, **kwargs): 
        super(AppForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

        if self.instance.pk:
            self.fields['confirmation_text'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['confirmation_text'].widget.mce_attrs['app_instance_id'] = 0


class AppFieldForm(forms.ModelForm):
    class Meta:
        model = AppField

    def __init__(self, *args, **kwargs):
        super(AppFieldForm, self).__init__(*args, **kwargs)

        # remove "admin only" option from membership type and payment method
        if self.instance.field_type in ['membership-type','payment-method']:
            self.fields['admin_only'] = BooleanField(widget=HiddenInput, required=False)

        # remove field_type options
        choices_dict = dict(self.fields['field_type'].choices)
        del choices_dict['membership-type']
        del choices_dict['payment-method']
        self.fields['field_type'].choices = choices_dict.items()

        # use hidden widget for membership-type
        if self.instance.field_type == 'membership-type':
            self.fields['field_type'] = CharField(label="Type", widget=HiddenInput)

        # user hidden widget for payment-method
        if self.instance.field_type == 'payment-method':
            self.fields['field_type'] = CharField(label="Type", widget=HiddenInput)
            
    
    def clean_function_params(self):
        function_params = self.cleaned_data['function_params']
        clean_params = ''
        for val in function_params.split(','):
            clean_params = val.strip() + ',' + clean_params
        return clean_params[0:len(clean_params)-1]
        
    def clean(self):
        cleaned_data = self.cleaned_data
        field_function = cleaned_data.get("field_function")
        function_params = cleaned_data.get("function_params")
        field_type = cleaned_data.get("field_type")
        
        if field_function == "Group":
            if field_type != "check-box":
                raise forms.ValidationError("This field's function requires Checkbox as a field type")
            if not function_params:
                raise forms.ValidationError("This field's function requires at least 1 group specified.")
            else:
                for val in function_params.split(','):
                    try:
                        Group.objects.get(name=val)
                    except Group.DoesNotExist:
                        raise forms.ValidationError("The group \"%s\" does not exist" % (val))
        
        return cleaned_data



class EntryEditForm(forms.ModelForm):

    class Meta:
        model = AppEntry
        exclude = (
            'entry_time',
            'allow_anonymous_view',
            'allow_anonymous_edit',
            'allow_user_view',
            'allow_user_edit',
            'allow_member_view',
            'allow_member_edit',
            'creator_username',
            'owner',
            'owner_username',
            'status',
            'status_detail'
        )

    def __init__(self, *args, **kwargs):
        super(EntryEditForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        entry_fields = AppFieldEntry.objects.filter(entry=instance)

        is_corporate = instance.membership_type and \
            instance.membership_type.corporatemembershiptype_set.exists()

        for entry_field in entry_fields:
            field_type = entry_field.field.field_type  # shorten
            field_key = "%s.%s" % (entry_field.field.field_type, entry_field.pk)

            field_class, field_widget = CLASS_AND_WIDGET[field_type]
            field_class = getattr(forms, field_class)

            arg_names = field_class.__init__.im_func.func_code.co_varnames
            field_args = {}

            field_args['label'] = entry_field.field.label
            field_args['initial'] = entry_field.value
            field_args['required'] = False

            if "max_length" in arg_names:
                field_args["max_length"] = FIELD_MAX_LENGTH

            if "choices" in arg_names:

                if field_type == 'membership-type':
                    choices = [t.name for t in instance.app.membership_types.all()]
                    choices_with_price = ['%s $%s' % (t.name, t.price) for t in instance.app.membership_types.all()]
                    field_args["choices"] = zip(choices, choices_with_price)

                    if is_corporate:  # membership type; read-only
                        del field_args["choices"]
                        field_class = getattr(forms, 'CharField') 
                        field_args["widget"] = forms.TextInput(attrs={'readonly':'readonly'})

                elif field_type == 'corporate_membership_id':
                    choices = [c.name for c in CorporateMembership.objects.all()]
                    field_args["choices"] = zip(choices, choices)
                else:
                    choices = entry_field.field.choices.split(',')
                    choices = [c.strip() for c in choices]
                    field_args["choices"] = zip(choices, choices)

            self.fields[field_key] = field_class(**field_args)

    def save(self, *args, **kwargs):
        super(EntryEditForm, self).save(*args, **kwargs)

        for key, value in self.cleaned_data.items():
            pk = key.split('.')[1]

            membership_type = None
            membership_type_entry_pk = 0

            if 'corporate_membership' in key:
                corp_memb = CorporateMembership.objects.get(name=value)  # get corp. via name
                membership_type = corp_memb.corporate_membership_type.membership_type

            if 'membership-type' in key:
                membership_type_entry_pk = pk

            AppFieldEntry.objects.filter(pk=pk).update(value=value)

            # update membership entry_field
            if membership_type and membership_type_entry_pk:
                AppFieldEntry.objects.filter(pk=membership_type_entry_pk).update(value=membership_type.name)

        # update membership.membership_type relationship
        if self.instance.membership and membership_type:
            self.instance.membership.membership_type = membership_type
            self.instance.save()

        return self.instance



class AppEntryForm(forms.ModelForm):

    class Meta:
        model = AppEntry
        exclude = (
            'entry_time',
            'allow_anonymous_view',
            'allow_anonymous_edit',
            'allow_user_view',
            'allow_user_edit',
            'allow_member_view',
            'allow_member_edit',
            'creator_username',
            'owner',
            'owner_username',
            'status',
            'status_detail'
        )

    def __init__(self, app=None, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model 
        instance and its related field model instances.
        """

        self.app = app
        
        self.types_field = app.membership_types
        self.user = kwargs.pop('user', None) or AnonymousUser
        self.corporate_membership = kwargs.pop('corporate_membership', None) # id; not object
        
        if is_admin(self.user):
            self.form_fields = app.fields.visible()
        else:
            self.form_fields = app.fields.non_admin_visible()

        super(AppEntryForm, self).__init__(*args, **kwargs)

        CLASS_AND_WIDGET = {
            'text': ('CharField', None),
            'paragraph-text': ('CharField', 'django.forms.Textarea'),
            'check-box': ('BooleanField', None),
            'choose-from-list': ('ChoiceField', None),
            'multi-select': ('MultipleChoiceField', 'django.forms.CheckboxSelectMultiple'),
            'email-field': ('EmailField', None),
            'file-uploader': ('FileField', None),
            'date': ('DateField', 'django.forms.extras.SelectDateWidget'),
            'date-time': ('DateTimeField', None),
            'membership-type': ('ChoiceField', 'django.forms.RadioSelect'),
            'payment-method': ('ChoiceField', None),
            'first-name': ('CharField', None),
            'last-name': ('CharField', None),
            'email': ('EmailField', None),
            'header': ('CharField', 'memberships.widgets.Header'),
            'description': ('CharField', 'memberships.widgets.Description'),
            'horizontal-rule': ('CharField', 'memberships.widgets.Description'),
            'corporate_membership_id': ('ChoiceField', None),
        }

        for field in self.form_fields:

            if field.field_type == 'corporate_membership_id' and not self.corporate_membership:
                continue  # on to the next one

            field_key = "field_%s" % field.id
            field_class, field_widget = CLASS_AND_WIDGET[field.field_type]
            field_class = getattr(forms, field_class)
            field_args = {"label": field.label, "required": field.required}
            arg_names = field_class.__init__.im_func.func_code.co_varnames

            if "max_length" in arg_names:
                field_args["max_length"] = FIELD_MAX_LENGTH

            if "choices" in arg_names:
                if field.field_type == 'membership-type':
                    if not self.corporate_membership:
                        choices = [type.name for type in app.membership_types.all()]
                        choices_with_price = ['%s $%s' % (type.name, type.price) for type in app.membership_types.all()]
                        field_args["choices"] = zip(choices, choices_with_price)
                    else:
                        membership_type = self.corporate_membership.corporate_membership_type.membership_type 
                        choices = [membership_type.name]
                        choices_with_price = ['%s $%s' % (membership_type.name, membership_type.price)]
                        field_args["choices"] = zip(choices, choices_with_price)
                elif field.field_type == 'corporate_membership_id' and self.corporate_membership:
                    field_args["choices"] = ((self.corporate_membership.id, self.corporate_membership.name),)
                else:
                    choices = field.choices.split(",")
                    choices = [c.strip() for c in choices]
                    field_args["choices"] = zip(choices, choices)

            if field.field_type == 'corporate_membership_id' and self.corporate_membership:
                pass
            else:
                field_args['initial'] = field.default_value
            field_args['help_text'] = field.help_text

            if field.pk in kwargs['initial']:
                field_args['initial'] = kwargs['initial'][field.pk]

            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)

            self.fields[field_key] = field_class(**field_args)
            self.fields[field_key].css_classes = ' %s' % field.css_class

            if field.field_type == 'date':
                year = datetime.today().year
                self.fields[field_key].widget.years = range(year-120, year+120)

        if app.use_captcha and not self.user.is_authenticated():
            self.fields['field_captcha'] = CaptchaField(**{
                'label':'',
                'error_messages':{'required':'CAPTCHA is required'}
                })


    def save(self, **kwargs):
        """
        Create a AppEntry instance and related AppFieldEntry instances for each 
        form field.
        """
        app_entry = super(AppEntryForm, self).save(commit=False)
        app_entry.app = self.app
        
        # TODO: We're assuming that an administrator exists
        # We're assuming this administrator is actively used
        admin = User.objects.order_by('pk')[0]
        
        user = None
        username = None
        if hasattr(self.user, 'pk'):
            user = self.user
            username = user.username
        
        app_entry.user = user
        app_entry.entry_time = datetime.now()
        app_entry.creator = user or admin
        app_entry.creator_username = username or admin.username
        app_entry.owner = user or admin
        app_entry.owner_username = username or admin.username
        app_entry.status = True
        app_entry.status_detail = 'active'
        app_entry.allow_anonymous_view = False
        
        app_entry.save()
        
        app_entry.hash = md5(unicode(app_entry.pk)).hexdigest()
        app_entry.save()
        
        #create all field entries
        for field in self.form_fields:
            if field.field_type == 'corporate_membership_id' and not self.corporate_membership:
                continue
            field_key = "field_%s" % field.id
            value = self.cleaned_data[field_key]
            if value and self.fields[field_key].widget.needs_multipart_form:
                value = fs.save(join("forms", str(uuid4()), value.name), value)
            # if the value is a list convert is to a comma delimited string
            if isinstance(value,list):
                value = ','.join(value)
            if not value: value=''
            app_entry.fields.create(field_id=field.id, value=value)
            
        return app_entry

    def email_to(self):
        """
        Return the value entered for the first field of type EmailField.
        """
        for field in self.form_fields:
            field_class = field.field_type.split("/")[0]
            if field_class == "EmailField":
                return self.cleaned_data["field_%s" % field.id]
        return None

class CSVForm(forms.Form):
    """
    Map CSV import to Membership Application.
    Create Membership Entry on save() method.
    """
    def __init__(self, *args, **kwargs):
        """
        Dynamically create fields using the membership
        application chosen.  The choices provided to these
        dynamic fields are the csv import columns.
        """
        step_numeral, step_name = kwargs.pop('step', (None, None))
        app = kwargs.pop('app', '')
        file_path = kwargs.pop('file_path', '')

        super(CSVForm, self).__init__(*args, **kwargs)

        if step_numeral == 1:
            """
            Basic Form: Application & File Uploader
            """
            
            self.fields['app'] = forms.ModelChoiceField(
                label='Application', queryset=App.objects.all())

            self.fields['csv'] = forms.FileField(label="CSV File")
        
        if step_numeral == 2:
            """
            Basic Form + Mapping Fields
            """

            # file to make field-mapping form
            csv = csv_to_dict(file_path)

            # choices list
            choices = csv[0].keys()

            # make tuples; sort tuples (case-insensitive)
            choice_tuples = [(c,c) for c in csv[0].keys()]

            choice_tuples.insert(0, ('',''))  # insert blank option
            choice_tuples = sorted(choice_tuples, key=lambda c: c[0].lower())

            app_fields = AppField.objects.filter(app=app)

            native_fields = [
                'User Name',
                'Membership Type',
                'Corp. Membership Name',
                'Member Number',
                'Payment Method',
                'Join Date',
                'Renew Date',
                'Expire Date',
                'Owner',
                'Creator',
                'Status',
                'Status Detail',
            ]

            for native_field in native_fields:
                self.fields[slugify(native_field)] = ChoiceField(**{
                    'label': native_field,
                    'choices': choice_tuples,
                    'required': False,
                })

                # compare required field with choices
                # if they match; set initial
                if native_field in choices:
                    self.fields[slugify(native_field)].initial = native_field

            self.fields['user-name'].required = True
            self.fields['membership-type'].required = True

            for app_field in app_fields:
                for csv_row in csv:

                    if slugify(app_field.label) == 'membership-type':
                        continue  # skip membership type

                    self.fields[app_field.label] = ChoiceField(**{
                        'label':app_field.label,
                        'choices': choice_tuples,
                        'required': False,
                    })

                    # compare label with choices
                    # if label matches choice; set initial
                    if app_field.label in choices:
                        self.fields[app_field.label].initial = app_field.label
   


    def save(self, *args, **kwargs):
        """
        Loop through the dynamic fields and create an 
        entry and membership record. Map application, 
        entry, and membership record.

        Checking app.pk, user.pk and entry_time to 
        recognize duplicates.
        """
        step_numeral, step_name = kwargs.pop('step', (None, None))

        if step_numeral == 1:
            """
            Basic Form: Application & File Uploader
            """
            return self.cleaned_data

        if step_numeral == 2:
            """
            Basic Form + Mapping Fields
            """
            pass  # mapping of fields
            return self.cleaned_data

        if step_numeral == 3:
            pass  # end-user is previewing

        if step_numeral == 4:
            memberships = request.session.get('membership.import.memberships')

            for membership in memberships:

                entry = AppEntry.objects.filter(
                    app = app,
                    user = user,
                    entry_time = datetime.now(),
                    membership = membership,
                ).exists()

                if not entry:  # create; if does not exist

                    entry = AppEntry.objects.create(
                        app = app,
                        user = user,
                        entry_time = datetime.now(),
                        membership = membership,
                        is_renewal = membership.renewal,
                        is_approved = True,
                        decision_dt = membership.create_dt,
                        judge = membership.creator,
                        creator=membership.creator,
                        creator_username=membership.creator_username,
                        owner=membership.owner,
                        owner_username=membership.owner_username,
                    )

                    for key, value in self.cleaned_data.items():

                        app_fields = AppField.objects.filter(app=app, label=key)
                        if app_fields:
                            app_field = app_fields[0]
                        else:
                            app_field = None

                        try:
                            AppFieldEntry.objects.create(
                                entry=entry,
                                field=app_field,
                                value=value,
                            )
                        except:
                            print sys.exc_info()[1]


class ExportForm(forms.Form):
    app = forms.ModelChoiceField(
                label=_('Application'), 
                queryset=App.objects.all())
    passcode = forms.CharField(label=_("Type Your Password"), 
                               widget=forms.PasswordInput(render_value=False))
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', '')
        super(ExportForm, self).__init__(*args, **kwargs)
        
    def clean_passcode(self):
        value = self.cleaned_data['passcode']
        
        if not self.user.check_password(value):
            raise forms.ValidationError(_("Invalid password."))
        return value

class ReportForm(forms.Form):
    STATUS_CHOICES = (
        ('', '----------'),
        ('ACTIVE', 'ACTIVE'),
        ('EXPIRED', 'EXPIRED'),
    )
    
    membership_type = forms.ModelChoiceField(queryset = MembershipType.objects.all(), required = False)
    membership_status = forms.ChoiceField(choices = STATUS_CHOICES, required = False)
