from django import forms
from django.utils.translation import ugettext_lazy as _

from memberships.fields import PriceInput
from models import CorporateMembershipType, CorpApp, CorpField

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
        

class CorpFieldForm(forms.ModelForm):
    class Meta:
        model = CorpField
        fields = (
                  'label',
                  #'field_name',
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