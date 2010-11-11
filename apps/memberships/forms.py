from uuid import uuid4
from os.path import join
from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.importlib import import_module
from perms.models import ObjectPermission
from perms.forms import TendenciBaseForm
from models import MembershipType, App, AppEntry, AppField, AppFieldEntry
from fields import TypeExpMethodField, PriceInput
from widgets import CustomRadioSelect
from perms.utils import is_admin
from memberships.settings import FIELD_MAX_LENGTH, UPLOAD_ROOT
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location=UPLOAD_ROOT)

type_exp_method_fields = ('period_type', 'period', 'period_unit', 'expiration_method', 
                        'expiration_method_day', 'renew_expiration_method', 'renew_expiration_day',
                        'renew_expiration_day2', 'fixed_expiration_method','fixed_expiration_day',
                        'fixed_expiration_month', 'fixed_expiration_year', 'fixed_expiration_day2',
                        'fixed_expiration_month2', 'fixed_expiration_rollover',
                        'fixed_expiration_rollover_days')
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

class MembershipTypeForm(forms.ModelForm):
    type_exp_method = TypeExpMethodField(label='Period Type')
    description = forms.CharField(label=_('Notes'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    price = forms.DecimalField(decimal_places=2, widget=PriceInput(), 
                               help_text="Set 0 for free membership.")
    admin_fee = forms.DecimalField(decimal_places=2, required=False,
                                   widget=PriceInput(),
                                   help_text="Admin fee for the first time processing")
    
    class Meta:
        model = MembershipType
        fields = (
                  'name',
                  'price',
                  'admin_fee',
                  'description',
                  'group',
                  #'period_type',
                  'type_exp_method',
                  #'c_period',
                  #'c_expiration_method',
                  'corporate_membership_only',
                  'corporate_membership_type_id',
                  'require_approval',
                  'renewal',
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
                if field == 'fixed_expiration_rollover' and (not field_value):
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
                d['expiration_method'] = int(d['expiration_method'])
            except:
                raise forms.ValidationError(_("Please select an expiration method."))
            if d['expiration_method'] not in [0, 1]:
                raise forms.ValidationError(_("Please select an expiration method."))
            if d['expiration_method'] == 1:
                try:
                    d['expiration_method_day'] = int(d['expiration_method_day'])
                except:
                    raise forms.ValidationError(_("Expiration day(s) at signup month must be a numeric number."))
            # renew expiration
            try:
                d['renew_expiration_method'] = int(d['renew_expiration_method'])
            except:
                raise forms.ValidationError(_("Please select a renew expiration method."))
            if d['renew_expiration_method'] not in [0, 1, 2]:
                raise forms.ValidationError(_("Please select a renew expiration method."))
            if d['expiration_method'] == 1:
                try:
                    d['renew_expiration_day'] = int(d['renew_expiration_day'])
                except:
                    raise forms.ValidationError(_("Renew expiration day(s) at signup month must be a numeric number."))
            if d['renew_expiration_method'] == 2:
                try:
                    d['renew_expiration_day2'] = int(d['renew_expiration_day2'])
                except:
                    raise forms.ValidationError(_("Renew expiration day(s) at renewal month must be a numeric number."))
        
        else: # d['period_type'] == 'fixed'
            try:
                d['fixed_expiration_method'] = int(d['fixed_expiration_method'])
            except:
                raise forms.ValidationError(_("Please select an expiration method for fixed period."))
            if d['fixed_expiration_method'] not in [0, 1]:
                raise forms.ValidationError(_("Please select an expiration method for fixed period."))
            if d['fixed_expiration_method'] == 0:
                try:
                    d['fixed_expiration_day'] = int(d['fixed_expiration_day'])
                except:
                    raise forms.ValidationError(_("Fixed expiration day(s) must be a numeric number."))
            if d['fixed_expiration_method'] == 1:
                try:
                    d['fixed_expiration_day2'] = int(d['fixed_expiration_day2'])
                except:
                    raise forms.ValidationError(_("Fixed expiration day(s) of current year must be a numeric number."))
                
            if d.has_key('fixed_expiration_rollover') and d['fixed_expiration_rollover']:
                try:
                    d['fixed_expiration_rollover_days'] = int(d['fixed_expiration_rollover_days'])
                except:
                    raise forms.ValidationError(_("Grace period day(s) must be a numeric number."))
           
        return value
    
    def save(self, *args, **kwargs):
        return super(MembershipTypeForm, self).save(*args, **kwargs)

class AppForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('draft','Draft'),('published','Published')))

    class Meta:
        model = App

class AppFieldForm(forms.ModelForm):
    class Meta:
        model = AppField

class AppEntryForm(forms.ModelForm):

    class Meta:
        model = AppEntry
        exclude = ("form", "entry_time",)

    def __init__(self, app, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model 
        instance and its related field model instances.
        """
        self.app = app
        self.form_fields = app.fields.visible()
        super(AppEntryForm, self).__init__(*args, **kwargs)

        for field in self.form_fields:
            field_key = "field_%s" % field.id
            if "/" in field.field_type:
                field_class, field_widget = field.field_type.split("/")
            else:
                field_class, field_widget = field.field_type, None
            field_class = getattr(forms, field_class)
            field_args = {"label": field.label, "required": field.required}
            arg_names = field_class.__init__.im_func.func_code.co_varnames
            if "max_length" in arg_names:
                field_args["max_length"] = FIELD_MAX_LENGTH
            if "choices" in arg_names:
                choices = field.choices.split(",")
                field_args["choices"] = zip(choices, choices)
            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)
            self.fields[field_key] = field_class(**field_args)

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
