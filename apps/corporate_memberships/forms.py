from django import forms
from django.utils.translation import ugettext_lazy as _

from memberships.fields import PriceInput
from models import CorporateMembershipType, CorpApp, CorpPage, CorpSection, CorpField

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
        
class CorpPageForm(forms.ModelForm):
    top_instruction = forms.CharField(label=_('Top Instruction'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    bottom_instruction = forms.CharField(label=_('Bottom Instruction'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    
    class Meta:
        model = CorpPage
        fields = (
                  'order',
                  'title',
                  'top_instruction',
                  'bottom_instruction',
                  'css_class',
                  )
        
class CorpSectionForm(forms.ModelForm):
    description = forms.CharField(label=_('Description'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    
    class Meta:
        model = CorpSection
        fields = (
                  'label',
                  'description',
                  'admin_only',
                  'css_class',
                  )
        
class CorpFieldForm(forms.ModelForm):
    field_name = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(),
                                label=_(u'Field Name'),
                                help_text = _("No space. Less than 30 characters. Letters, digits and underscores only."))
    
    class Meta:
        model = CorpField
        fields = (
                  'label',
                  'field_name',
                  'field_type',
                  'size',
                  'choices',
                  'field_layout',
                  'required',
                  'visible',
                  'no_duplicates',
                  'help_text',
                  'default_value',
                  'admin_only',
                  'css_class',
                  )