from django import forms
from django.utils.translation import ugettext_lazy as _

from models import MembershipType
from fields import TypeExpMethodField, TypeExpMethodWidget, PriceInput
#from fields import PeriodField, PeriodWidget, PriceInput, JoinExpMethodWidget, JoinExpMethodField

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
                        forms.RadioSelect(),
                        forms.TextInput(),
                        forms.RadioSelect(),
                        forms.TextInput(),
                        forms.TextInput(),
                        forms.RadioSelect(),
                        forms.Select(),
                        forms.Select(),
                        forms.Select(),
                        forms.Select(),
                        forms.Select(),
                        forms.CheckboxInput(),
                        forms.TextInput(),
                        )

class MembershipTypeForm(forms.ModelForm):
    # custom fields: period, expiration_method, renew_expiration_method, 
    # fixed_expiration_method, fixed_expiration_rollover
    #c_period = PeriodField(widget=PeriodWidget(attrs={'id':'period'}), 
    #                       initial="1,months", label='Period')
    #c_expiration_method = JoinExpMethodField(widget=JoinExpMethodWidget(), required=False,
    #                                         label='Expires On')
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
                initial_list.append(str(eval('self.instance.%s' % field)))
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
        
        # TODO: more work later
        return value
    
    def save(self, *args, **kwargs):
        return super(MembershipTypeForm, self).save(*args, **kwargs)
        
