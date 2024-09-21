from django import forms
from tendenci.apps.payments.models import Payment
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.entities.models import Entity
from .models import StripeAccount
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.fields import StateSelectField
#from form_utils.forms import BetterModelForm


class AccountOnBoardingForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = StripeAccount
        fields = ('account_name',
                  'email',
                  'scope' )


class StripeAccountForm(forms.ModelForm):
    entity = forms.ModelChoiceField(queryset=Entity.objects.order_by('entity_name'))

    class Meta:
        model = StripeAccount
        fields = ('stripe_user_id', 'scope',
                  'account_name', 'email', 
                  'entity',
                'default_currency',
                'status_detail')


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
        # state
        if get_setting('site', 'global', 'stateusesdropdown'):
            self.fields['state'] = StateSelectField(label=self.fields['state'].label,
                                                    required=self.fields['state'].required)
            self.fields['state'].widget.attrs.update({'class': 'form-control'})
