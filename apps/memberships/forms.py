import operator
from uuid import uuid4
from captcha.fields import CaptchaField
from django.contrib.auth.models import AnonymousUser
from django.forms.fields import CharField
from django.forms.widgets import HiddenInput
from haystack.query import SearchQuerySet
from os.path import join
from datetime import datetime

from django.http import Http404
from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.importlib import import_module
from django.core.files.storage import FileSystemStorage

from tinymce.widgets import TinyMCE

from perms.forms import TendenciBaseForm
from models import MembershipType, Notice, App, AppEntry, AppField
from fields import TypeExpMethodField, PriceInput
from memberships.settings import FIELD_MAX_LENGTH, UPLOAD_ROOT
from widgets import CustomRadioSelect, TypeExpMethodWidget, NoticeTimeTypeWidget
from corporate_memberships.models import CorporateMembership, AuthorizedDomain

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

    #    full_name_q = Q(content='%s %s' % (mentioned_fn, mentioned_ln))
        email_q = Q(content=mentioned_em)
    #    q = reduce(operator.or_, [full_name_q, email_q])
        sqs = sqs.filter(email_q)

        sqs_users = [sq.object.user for sq in sqs]

        for u in sqs_users:
            user_set[u.pk] = '%s %s %s %s' % (u.first_name, u.last_name, u.username, u.email)
            self.fields['users'].initial = u.pk

        user_set[0] = 'Create new user'

        return user_set.items()

    def __init__(self, entry, *args, **kwargs):
        super(MemberApproveForm, self).__init__(*args, **kwargs)

        self.entry = entry
        suggested_users = entry.suggested_users(grouping=[('email',)])
        suggested_users.append((0, 'Create new user'))
        self.fields['users'].choices = suggested_users
        self.fields['users'].initial = 0

#        self.fields['users'].choices = self.get_suggestions(entry)

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
            #print self.fields['type_exp_method'].initial
  
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
    notice_time_type = TypeExpMethodField(label='When to Send',
                                          widget=NoticeTimeTypeWidget)
    email_content = forms.CharField(widget=TinyMCE(attrs={'style':'width:70%'}, 
                                            mce_attrs={'storme_app_label':"email_content", 
                                                       'storme_model':"email_content"}))
    
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
        
        initial_list = []
        if self.instance.pk:
            initial_list.append(str(self.instance.num_days))
            initial_list.append(str(self.instance.notice_time))
            initial_list.append(str(self.instance.notice_type))
        
        self.fields['notice_time_type'].initial = initial_list
        
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
    email = forms.EmailField(label=_('Enter Your Email Address'), max_length=100,
                             help_text="Your email address will help us to find your corporation.")
    
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
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            email_domain = (email.split('@')[1]).strip()
            auth_domains = AuthorizedDomain.objects.filter(name=email_domain)
            if not auth_domains:
                raise forms.ValidationError(_("Sorry but we're not able to find your corporation."))
            self.corporate_membership_id = auth_domains[0].corporate_membership.id  

class AppForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('draft','Draft'),('published','Published')))

    class Meta:
        model = App

class AppFieldForm(forms.ModelForm):
    class Meta:
        model = AppField

    def __init__(self, *args, **kwargs):
        super(AppFieldForm, self).__init__(*args, **kwargs)

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

class AppEntryForm(forms.ModelForm):

    class Meta:
        model = AppEntry
        exclude = ("entry_time",)

    def __init__(self, app=None, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model 
        instance and its related field model instances.
        """
        self.app = app
        self.form_fields = app.fields.visible()
        self.types_field = app.membership_types
        
        user = kwargs.pop('user', AnonymousUser)
        # corporate_membership_id for corp. individuals
        self.corporate_membership = kwargs.pop('corporate_membership', None)

        super(AppEntryForm, self).__init__(*args, **kwargs)

        CLASS_AND_WIDGET = {
            'text': ('CharField', None),
            'paragraph-text': ('CharField', 'django.forms.Textarea'),
            'check-box': ('BooleanField', None),
            'choose-from-list': ('ChoiceField', None),
            'multi-select': ('BooleanField', None),
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
                continue
                
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

            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)

            self.fields[field_key] = field_class(**field_args)
            self.fields[field_key].css_classes = ' %s' % field.css_class

        if app.use_captcha and not user.is_authenticated():
            self.fields['field_captcha'] = CaptchaField(**{
                'label':'',
                'error_messages':{'required':'CAPTCHA is required'}
                })


    def save(self, **kwargs):
        """
        Create a FormEntry instance and related FieldEntry instances for each 
        form field.
        """
        app_entry = super(AppEntryForm, self).save(commit=False)
        app_entry.app = self.app
        app_entry.entry_time = datetime.now()
        app_entry.save()

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
    app = forms.ModelChoiceField(label='Application', queryset=App.objects.all())
    csv = forms.FileField(label="CSV File")
    
class ReportForm(forms.Form):
    STATUS_CHOICES = (
        ('', '----------'),
        ('ACTIVE', 'ACTIVE'),
        ('EXPIRED', 'EXPIRED'),
    )
    
    membership_type = forms.ModelChoiceField(queryset = MembershipType.objects.all(), required = False)
    membership_status = forms.ChoiceField(choices = STATUS_CHOICES, required = False)
