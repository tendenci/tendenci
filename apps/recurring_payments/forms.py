from django import forms

from models import RecurringPayment
from memberships.fields import PriceInput

class RecurringPaymentForm(forms.ModelForm):
    status_detail = forms.ChoiceField(choices=(('inactive','Inactive'),('active','Active')),
                                      initial='active')
    billing_frequency = forms.IntegerField(initial=1, help_text="If billing frequency is 2" + \
                                           " and billing period is Month, payment will" + \
                                            " be made every 2 months.")
    payment_amount = forms.DecimalField(decimal_places=2, widget=PriceInput())
    trial_amount = forms.DecimalField(decimal_places=2, widget=PriceInput(), required=False)
    
    class Meta:
        model = RecurringPayment
        fields = ('user', 
                  'description',
                  'billing_period',
                  'billing_frequency',
                  'billing_cycle_start_dt',
                  'billing_cycle_end_dt',
                  'payment_amount',
                  'has_trial_period',
                  'trial_period_start_dt',
                  'trial_period_end_dt',
                  'trial_amount',
                  'status',
                  'status_detail',
                  )
