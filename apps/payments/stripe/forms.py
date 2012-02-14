from django import forms
from widgets import NoNameTextInput
from payments.models import Payment


class StripeCardForm(forms.Form):
    card_number = forms.CharField(required=False, max_length=20,
                                  widget=NoNameTextInput())
    card_cvc = forms.CharField(required=False, max_length=4,
                               widget=NoNameTextInput())
    card_expiry_month = forms.CharField(required=False, max_length=2,
                                widget=NoNameTextInput())
    card_expiry_year = forms.CharField(required=False, max_length=4,
                                widget=NoNameTextInput())
    
    stripe_token = forms.CharField(required=True, widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(StripeCardForm, self).__init__(*args, **kwargs)
        self.fields['card_cvc'].label = "Card CVC"
        self.fields['card_cvc'].help_text = "Card Verification Code"
        
class BillingInfoForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('first_name',
                  'last_name', 
                  'email',
                  'email',
                  'company',
                  'address',
                  'address2',
                  'city',
                  'state',
                  'zip',
                  'country',
                  'phone',
                  'fax',
                  )