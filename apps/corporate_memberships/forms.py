from django import forms
from django.utils.translation import ugettext_lazy as _

from memberships.fields import PriceInput
from models import CorporateMembershipType, CorpApp, CorpField, CorporateMembership
from corporate_memberships.utils import get_corpapp_default_fields_list

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
    notes = forms.CharField(label=_('Notes'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('admin hold','Admin Hold'),))
    
    class Meta:
        model = CorpApp
        fields = (
                  'name',
                  'slug',
                  'corp_memb_type',
                  'authentication_method',
                  'notes',
                  'use_captcha',
                  'require_login',
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
    field_name = forms.CharField(label=_(''), max_length=30, required=False,
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
    
    
class CorpAppPreviewForm(forms.ModelForm):
    class Meta:
        model = CorporateMembership
        exclude = ('cma', 'guid', 'renewal', 'invoice', 'renew_dt', 
                   'expiration_dt', 'approved', 'approved_denied_dt',
                   'approved_denied_user', )
        
    def __init__(self, corpapp, *args, **kwargs):
        """
            Dynamically build the form fields.
        """
        self.cma = corpapp
        self.form_fields = corpapp.fields.filter(visible=1).order_by('order')
        super(CorpAppPreviewForm, self).__init__(*args, **kwargs)
        
        for field in self.form_fields:
            if field.field_name:
                field_key = field.field_name
            else:
                field_key = "field_%s" % field.id
            
            self.fields[field_key] = field.get_field_class()
        
        
            
        