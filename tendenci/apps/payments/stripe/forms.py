from django import forms
from tendenci.apps.payments.models import Payment
from tendenci.apps.base.forms import FormControlWidgetMixin
#from form_utils.forms import BetterModelForm


class StripeCardForm(forms.Form):
    stripe_token = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}))


class BillingInfoForm(FormControlWidgetMixin, forms.ModelForm):
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
        self.fields['address2'].width = 7
        self.fields['state'].width = 5
        self.fields['zip'].required = True
        self.fields['zip'].width = 7
