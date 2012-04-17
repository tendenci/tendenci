from uuid import uuid4
from os.path import join
from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.forms.fields import ChoiceField
#from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str

#from captcha.fields import CaptchaField
from tinymce.widgets import TinyMCE

from memberships.fields import PriceInput
from models import (CorporateMembershipType, 
                    CorpApp, 
                    CorpField, 
                    CorporateMembership, 
                    CorporateMembershipRep, 
                    CorpMembRenewEntry)
from corporate_memberships.utils import (get_corpapp_default_fields_list, 
                                         update_auth_domains, 
                                         get_payment_method_choices,
                                         get_indiv_membs_choices,
                                         get_corporate_membership_type_choices,
                                         csv_to_dict)
from corporate_memberships.settings import FIELD_MAX_LENGTH, UPLOAD_ROOT
from base.fields import SplitDateTimeField
from perms.utils import is_admin
from payments.models import PaymentMethod

fs = FileSystemStorage(location=UPLOAD_ROOT)


class CorporateMembershipTypeForm(forms.ModelForm):
    description = forms.CharField(label=_('Description'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    price = forms.DecimalField(decimal_places=2, widget=PriceInput(), 
                               help_text="Set 0 for free membership.")
    renewal_price = forms.DecimalField(decimal_places=2, widget=PriceInput(), required=False, 
                               help_text="Set 0 for free membership.")
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('admin hold','Admin Hold'),))
    
    class Meta:
        model = CorporateMembershipType
        fields = (
                  'name',
                  'price',
                  'renewal_price',
                  'membership_type',
                  'description',
                  'apply_threshold',
                  'individual_threshold',
                  'individual_threshold_price',
                  'admin_only',
                  'order',
                  'status',
                  'status_detail',
                  )
        
class CorpAppForm(forms.ModelForm):
    description = forms.CharField(required=False,
                             widget=TinyMCE(attrs={'style':'width:70%'}, 
                                            mce_attrs={'storme_app_label':CorpApp._meta.app_label, 
                                                       'storme_model':CorpApp._meta.module_name.lower()}),
                                                       help_text='Will show at the top of the application form.')
    confirmation_text = forms.CharField(required=False,
                             widget=TinyMCE(attrs={'style':'width:70%'}, 
                                            mce_attrs={'storme_app_label':"confirmation_text", 
                                                       'storme_model':"confirmation_text"}),
                                                       help_text='Will show on the confirmation page.')
    notes = forms.CharField(label=_('Notes'), required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}),
                               help_text='Notes for editor. Will not display on the application form.')
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('admin hold','Admin Hold'),))
    
    class Meta:
        model = CorpApp
        fields = (
                  'name',
                  'slug',
                  'corp_memb_type',
                  'authentication_method',
                  'memb_app',
                  'payment_methods',
                  'description',
                  'confirmation_text',
                  'notes',
                  #'use_captcha',
                  #'require_login',
                  'status',
                  'status_detail',
                  )
        

default_corpapp_inline_fields_list = get_corpapp_default_fields_list()
if default_corpapp_inline_fields_list:
    required_corpapp_inline_fields_list = [str(field_d['field_name']) for field_d in default_corpapp_inline_fields_list if field_d['required']]
else:
    required_corpapp_inline_fields_list = []
    
class CorpFieldForm(forms.ModelForm):
    instruction = forms.CharField(label=_('Instruction for User'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    field_name = forms.CharField(label=(''), max_length=30, required=False,
                               widget=forms.HiddenInput())
    
    class Meta:
        model = CorpField
        fields = (
                  'label',
                  'field_name',
                  #'object_type',
                  'field_type',
                  'size',
                  'choices',
                  'field_layout',
                  'required',
                  'visible',
                  'no_duplicates',
                  'instruction',
                  'default_value',
                  'admin_only',
                  'css_class',
                  'order'
                  )
        
    def __init__(self, *args, **kwargs): 
        super(CorpFieldForm, self).__init__(*args, **kwargs)
        
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if instance.field_name in required_corpapp_inline_fields_list and instance.required:
                self.fields['required'].widget.attrs['disabled'] = "disabled"
                self.fields['visible'].widget.attrs['disabled'] = "disabled"
            if instance.field_name == 'name':
                self.fields['no_duplicates'].widget.attrs['disabled'] = "disabled"
                
    def clean_required(self):
        if self.instance.field_name in required_corpapp_inline_fields_list and self.instance.required:
            return self.instance.required
        return self.cleaned_data['required']
        
    def clean_visible(self):
        if self.instance.field_name in required_corpapp_inline_fields_list and self.instance.visible:
            return self.instance.visible
        return self.cleaned_data['visible']
    
    def clean_no_duplicates(self):
        if self.instance.field_name == 'name' and self.instance.no_duplicates:
            return self.instance.no_duplicates
        return self.cleaned_data['no_duplicates']
    
    
class CorpMembForm(forms.ModelForm):
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),
                 ('pending','Pending'),
                 ('paid - pending approval','Paid - Pending Approval'),
                 ('admin hold','Admin Hold'),
                 ('inactive','Inactive'), 
                 ('expired','Expired'),))
    join_dt = SplitDateTimeField(label=_('Join Date/Time'),
        initial=datetime.now())
    expiration_dt = SplitDateTimeField(label=_('Expiration Date/Time'), required=False,
                                       help_text='Not specified = Never expires')
    
    class Meta:
        model = CorporateMembership
        exclude = ('corp_app', 'guid', 'renewal', 'invoice', 'renew_dt', 'secret_code',
                   'approved', 'approved_denied_dt',
                   'approved_denied_user',
                   'creator_username', 'owner', 'owner_username')
        
    def __init__(self, corp_app, field_objs, *args, **kwargs):
        """
            Dynamically build the form fields.
        """
        self.corp_app = corp_app
        self.field_objs = field_objs
        super(CorpMembForm, self).__init__(*args, **kwargs)

        for field in field_objs:
            if field.field_type not in ['section_break', 'page_break']:
                if field.field_name:
                    field_key = field.field_name
                else:
                    field_key = "field_%s" % field.id
                    
                # if field is display only, remove it from the form
                # for example, on the edit page, we set corporate_membership_type
                # and payment_method as the display only fields
                if hasattr(field, 'display_only') and field.display_only:
                    del self.fields[field_key]
                else:
                
                    # get field class and set field initial
                    self.fields[field_key] = field.get_field_class()
                    if ((not field.field_name) or field.field_name=='authorized_domains') and self.instance:
                        initial = field.get_value(self.instance)
                        if field.field_type in ['MultipleChoiceField/django.forms.CheckboxSelectMultiple', 
                                                'MultipleChoiceField']:
                            if initial:
                                self.fields[field_key].initial = [item.strip() for item in initial.split(',')]
                        else:
                            self.fields[field_key].initial = initial
                    
         
        #self.fields['captcha'] = CaptchaField(label=_('Type the code below'))
        
    def clean_corporate_membership_type(self):
        if self.cleaned_data['corporate_membership_type']:
            return CorporateMembershipType.objects.get(pk=int(self.cleaned_data['corporate_membership_type']))
        return self.cleaned_data['corporate_membership_type']
    
    def clean_secret_code(self):
        secret_code = self.cleaned_data['secret_code']
        if secret_code:
            # check if this secret_code is available to ensure the uniqueness
            corp_membs = CorporateMembership.objects.filter(secret_code=secret_code)
            if self.instance:
                corp_membs = corp_membs.exclude(id=self.instance.id)
            if corp_membs:
                raise forms.ValidationError(_("This secret code is already taken. Please use a different one."))
        return self.cleaned_data['secret_code']
    
    def clean_payment_method(self):
        if self.cleaned_data['payment_method']:
            return PaymentMethod.objects.get(pk=int(self.cleaned_data['payment_method']))
        return self.cleaned_data['payment_method']
        
    def save(self, user,  **kwargs):
        """
            Create a CorporateMembership instance and related CorpFieldEntry instances for each 
            form field.
        """
        corporate_membership = super(CorpMembForm, self).save(commit=False)
        corporate_membership.corp_app = self.corp_app
        
        corporate_membership.owner = user
        corporate_membership.owner_username = user.username
        
        if not self.instance.pk:
            mode = 'add'
        else:
            mode = 'edit'
            
        if mode == 'add':
            corporate_membership.creator = user
            corporate_membership.creator_username = user.username
            
            if not is_admin(user):
                corporate_membership.status = 1
                corporate_membership.status_detail = 'pending'
                corporate_membership.join_dt = datetime.now()
            
            # calculate the expiration dt
        corporate_membership.save()
        for field_obj in self.field_objs:
            if (not field_obj.field_name) and field_obj.field_type not in ['section_break', 'page_break']:
                field_key = "field_%s" % field_obj.id
                value = self.cleaned_data[field_key]
                if value and self.fields[field_key].widget.needs_multipart_form:
                    if not type(value) is unicode:
                        value = fs.save(join("forms", str(uuid4()), value.name), value)
                # if the value is a list convert is to a comma delimited string
                if isinstance(value,list):
                    value = ','.join(value)
                if not value: value=''
                
                if hasattr(field_obj, 'entry') and field_obj.entry:
                    field_obj.entry.value = value
                    field_obj.entry.save()
                else:
                    corporate_membership.fields.create(field_id=field_obj.id, value=value)
                    
        # update authorized domain if needed
        if self.corp_app.authentication_method == 'email':
            update_auth_domains(corporate_membership, self.cleaned_data['authorized_domains'])
        
        return corporate_membership
    
    
class CorpMembRepForm(forms.ModelForm):
    user_display = forms.CharField(max_length=100, required=False,
                                    help_text='type name, or username or email')
    
    class Meta:
        model = CorporateMembershipRep
        fields=('user_display',
                'user',
                'is_dues_rep', 
                'is_member_rep',)
#        exclude = (
#                  'corporate_membership',
#                  )
        
    def __init__(self, corp_memb, *args, **kwargs):
        self.corporate_membership = corp_memb
        super(CorpMembRepForm, self).__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        #self.fields['user'].queryset = User.objects.filter(is_active=1)
#        users = User.objects.filter(is_active=1)
#        self.fields['user'].choices = [(0, 'Select One')] + [(u.id, '%s %s (%s)' % (u.first_name, 
#                                                                                    u.last_name, 
#                                                                                    u.email)) for u in users]
        self.fields['user_display'].label = "Add a Representative"
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].error_messages['required']='Please enter a valid user.'
        
    def clean_user(self):
        value = self.cleaned_data['user']
        try:
            rep = CorporateMembershipRep.objects.get(corporate_membership=self.corporate_membership, 
                                                     user=value)
            raise forms.ValidationError(_("This user is already a representative."))
        except CorporateMembershipRep.DoesNotExist:
            pass
        return value
    
    
class RosterSearchForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.HiddenInput())
    q = forms.CharField(max_length=100, required=False)
    
    
class CorpMembRenewForm(forms.ModelForm):
    members = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, 
                                        choices=[],required=False)
    select_all_members = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    
    class Meta:
        model = CorpMembRenewEntry
        fields = ('corporate_membership_type',
                  'members',
                  'payment_method',
                  'select_all_members')
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        corporate_membership = kwargs.pop('corporate_membership', None)
        
        super(CorpMembRenewForm, self).__init__(*args, **kwargs)
        
        self.fields['corporate_membership_type'].widget=forms.RadioSelect(choices=get_corporate_membership_type_choices(user, 
                                                                                                                        corporate_membership.corp_app, 
                                                                                                                        renew=True))
        self.fields['corporate_membership_type'].empty_label=None
        self.fields['corporate_membership_type'].initial = corporate_membership.corporate_membership_type.id
        
        members_choices = get_indiv_membs_choices(corporate_membership)
        self.fields['members'].choices = members_choices
        self.fields['members'].label = "Select the individual members you want to renew"
        
        self.fields['payment_method'].widget=forms.RadioSelect(choices=get_payment_method_choices(user, corporate_membership.corp_app))
        self.fields['payment_method'].empty_label=None
        self.fields['payment_method'].initial = corporate_membership.payment_method
        #self.fields['payment_method'].choices = get_payment_method_choices(user)
    

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
        corp_app = kwargs.pop('corp_app', '')
        file_path = kwargs.pop('file_path', '')

        super(CSVForm, self).__init__(*args, **kwargs)

        if step_numeral == 1:
            """
            Basic Form: Application & File Uploader
            """
            
            self.fields['corp_app'] = forms.ModelChoiceField(
                label=_('Corp Application'), queryset=CorpApp.objects.all())
            
            self.fields['update_option'] = forms.CharField(widget=forms.RadioSelect(
                                                choices=(('skip','Skip'),
                                                         ('update','Update Blank Fields'),
                                                        ('override','Override All Fields'),)), 
                                                initial='skip', 
                                                label=_('Select an Option for the Existing Records:'))

            self.fields['csv'] = forms.FileField(label=_("CSV File"))
            
            
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

            app_fields = CorpField.objects.filter(corp_app=corp_app)
            required_fields = ['name', 'corporate_membership_type']
            for field in app_fields:
                if field.field_type not in ['section_break', 'page_break']:
                    if field.field_name:
                        field_key = field.field_name
                    else:
                        field_key = "field_%s" % field.id
                    is_required = False
                    if field_key in required_fields:
                        is_required = True
                    self.fields[field_key] = ChoiceField(**{
                                                'label':field.label,
                                                'choices': choice_tuples,
                                                'required': is_required,
                                                })
                    for choice in choices:
                        if (field.label).lower() == choice.lower() or field_key.lower() == choice.lower():
                            self.fields[field_key].initial = choice
                    

            extra_fields = (('secret_code', 'Secret Code'),
                            ('join_dt', 'Join Date'),
                            ('renew_dt', 'Renew Date'),
                            ('expiration_dt', 'Expiration Date'),
                            ('approved','Approved'),
                            ('dues_rep','Dues Representative'),
                            ('status', 'Status'),
                            ('status_detail', 'Status Detail'))
            #corp_memb_field_names = [smart_str(field.name) for field in CorporateMembership._meta.fields]
            for key, label in extra_fields:
                if key not in self.fields.keys():
                    self.fields[key] = ChoiceField(**{
                                            'label':label,
                                            'choices': choice_tuples,
                                            'required': False,
                                            })
                    for choice in choices:
                        if label.lower() == choice.lower() or key.lower() == choice.lower():
                            self.fields[key].initial = choice
                    


    def save(self, *args, **kwargs):
        """
        Loop through the dynamic fields and create a corporate membership record.
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
            return self.cleaned_data

        if step_numeral == 3:
            pass  # end-user is previewing

class ExportForm(forms.Form):
    corp_app = forms.ModelChoiceField(
                label=_('Corp Application'), 
                queryset=CorpApp.objects.all())
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

        