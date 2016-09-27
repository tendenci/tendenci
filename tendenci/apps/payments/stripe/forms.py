from django import forms
from widgets import NoNameTextInput
from tendenci.apps.payments.models import Payment
#from form_utils.forms import BetterModelForm


class StripeCardForm(forms.Form):
    card_number = forms.CharField(required=False, max_length=20,
                                  widget=NoNameTextInput())
    card_name = forms.CharField(required=False, max_length=100,
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
        self.fields['card_number'].widget.attrs.update({'autocomplete': 'off'})
        self.fields['card_cvc'].label = "Card Code"
        self.fields['card_cvc'].help_text = """
                <a onclick="javascript:return PopupLink(this);"
                target="_blank" href="%s">What's this?</a>
                """ % 'https://account.authorize.net/help/Miscellaneous/Pop-up_Terms/hosted/Card_Code.htm'
        self.fields['card_cvc'].widget.attrs.update({'autocomplete': 'off',
                                                     'size': '4'})
        self.fields['card_expiry_month'].widget.attrs.update({'size': '2'})
        self.fields['card_expiry_year'].widget.attrs.update({'size': '4'})


class BillingInfoForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('first_name',
                  'last_name',
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

    def __init__(self, *args, **kwargs):
        super(BillingInfoForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'size': '30'})
        self.fields['last_name'].widget.attrs.update({'size': '30'})
        self.fields['email'].widget.attrs.update({'size': '30'})
        self.fields['company'].widget.attrs.update({'size': '30'})
        self.fields['address'].widget.attrs.update({'size': '30'})
        self.fields['address2'].widget.attrs.update({'size': '30'})
        self.fields['city'].widget.attrs.update({'size': '30'})
        self.fields['country'].widget.attrs.update({'size': '30'})
        self.fields['state'].widget.attrs.update({'size': '10'})
        self.fields['zip'].widget.attrs.update({'size': '10'})
        self.fields['phone'].widget.attrs.update({'size': '10'})
        self.fields['fax'].widget.attrs.update({'size': '10'})
