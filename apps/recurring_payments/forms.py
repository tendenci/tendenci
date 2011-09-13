from django import forms

from models import RecurringPayment
from memberships.fields import PriceInput
from widgets import BillingCycleWidget, BillingDateSelectInput
from fields import BillingCycleField

class RecurringPaymentForm(forms.ModelForm):
    #status_detail = forms.ChoiceField(choices=(('inactive','Inactive'),('active','Active')),
    #                                  initial='active')
    payment_amount = forms.DecimalField(decimal_places=2, widget=PriceInput())
    trial_amount = forms.DecimalField(decimal_places=2, widget=PriceInput(), required=False)
    
    num_days = forms.IntegerField(label='When to bill',
                                          widget=BillingDateSelectInput(attrs={'size': 3}), 
                                          help_text='It is used to determine the payment due date for each billing cycle')
    billing_cycle = BillingCycleField(label='How often to bill',
                                          widget=BillingCycleWidget)
    
    class Meta:
        model = RecurringPayment
        fields = ('user', 
                  'description',
                  'payment_amount',
                  'billing_start_dt',
                  'billing_cycle',
                  'num_days',
                  'has_trial_period',
                  'trial_period_start_dt',
                  'trial_period_end_dt',
                  'trial_amount',
                  'status',
                  'status_detail',
                  )
        
    def __init__(self, *args, **kwargs): 
        super(RecurringPaymentForm, self).__init__(*args, **kwargs)
        
        
        if self.instance.pk:
            initial_list= [str(self.instance.billing_frequency), 
                           str(self.instance.billing_period)]
        else:
            initial_list= ['1', 'month']
        
        self.fields['billing_cycle'].initial = initial_list
        
    
    def clean_billing_cycle(self):
        value = self.cleaned_data['billing_cycle']
        
        data_list = value.split(',')
        d = dict(zip(['billing_frequency', 'billing_period'], data_list))
        
        try:
            d['billing_frequency'] = int(d['billing_frequency'])
        except:
            raise forms.ValidationError(_("Billing frequency must be a numeric number."))
        return value
