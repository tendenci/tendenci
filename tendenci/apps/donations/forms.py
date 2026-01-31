from decimal import Decimal
from django import forms
from django.utils.translation import gettext_lazy as _
from tendenci.apps.donations.models import Donation
from tendenci.apps.donations.utils import get_allocation_choices, get_payment_method_choices, get_preset_amount_choices
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.entities.models import Entity
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.base.utils import tcurrency
from tendenci.libs.form_utils.forms import BetterModelForm
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.base.fields import StateSelectField, EmailVerificationField


class DonationAdminForm(forms.ModelForm):
    # get the payment_method choices from settings
    donation_amount = forms.CharField(error_messages={'required': _('Please enter the donation amount.')})
    payment_method = forms.CharField(error_messages={'required': _('Please select a payment method.')},
                                     widget=forms.RadioSelect(choices=(('check-paid', _('Paid by Check')),
                                                              ('cc', _('Make Online Payment')),)), initial='cc', )
    company = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'size':'30'}))
    address = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'size':'35'}))
    state = forms.CharField(max_length=50, required=False,  widget=forms.TextInput(attrs={'size':'5'}))
    zip_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'size':'10'}))
    referral_source = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'size':'40'}))
    email = forms.EmailField(help_text=_('A valid e-mail address, please.'))
    email_receipt = forms.BooleanField(initial=True)
    comments = forms.CharField(max_length=1000, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    #allocation = forms.ChoiceField()

    class Meta:
        model = Donation
        fields = ('donation_amount',
                  'payment_method',
                  'user',
                  'first_name',
                  'last_name',
                  'company',
                  'address',
                  'address2',
                  'city',
                  'state',
                  'zip_code',
                  'country',
                  'phone',
                  'email',
                  'email_receipt',
                  'donate_to_entity',
                  'referral_source',
                  'comments',
                  )

    def __init__(self, *args, **kwargs):
        # if 'user' in kwargs:
        #     self.user = kwargs.pop('user', None)
        # else:
        #     self.user = None
        super(DonationAdminForm, self).__init__(*args, **kwargs)
        self.fields['user'].required = False

        # donate_to_entity or allocation
        entity_qs = Entity.objects.filter(show_for_donation=True)
        self.fields['donate_to_entity'].queryset = entity_qs
        self.fields['donate_to_entity'].empty_label = _("Select One")
        self.fields['donate_to_entity'].label = _('Donate to')
        self.fields['donate_to_entity'].required = False

        preset_amount_str = (get_setting('module', 'donations', 'donationspresetamounts')).strip('')
        if preset_amount_str:
            self.fields['donation_amount'] = forms.ChoiceField(choices=get_preset_amount_choices(preset_amount_str))

        # check required fields
        required_fields = get_setting('module', 'donations', 'requiredfields')
        if required_fields:
            required_fields_list = [field.strip() for field in required_fields.split(',') if field.strip()]
            for field_name in required_fields_list:
                if field_name in self.fields:
                    self.fields[field_name].required = True


    def clean_donation_amount(self):
        try:
            if float(self.cleaned_data['donation_amount']) <= 0:
                raise forms.ValidationError(_(u'Please enter a positive number'))
        except:
            raise forms.ValidationError(_(u'Please enter a numeric positive number'))
        return self.cleaned_data['donation_amount']

class DonationForm(FormControlWidgetMixin, BetterModelForm):
    # get the payment_method choices from settings
    donation_amount = forms.CharField(error_messages={'required': _('Please enter the donation amount.')})
    payment_method = forms.CharField(error_messages={'required': _('Please select a payment method.')},
                                     widget=forms.RadioSelect(choices=(('check-paid', _('Paid by Check')),
                                                              ('cc', _('Make Online Payment')),)), initial='cc', )
    company = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'size':'30'}))
    address = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'size':'35'}))
    state = forms.CharField(max_length=50, required=False,  widget=forms.TextInput(attrs={'size':'5'}))
    zip_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'size':'10'}))
    referral_source = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'size':'40'}))
    email = EmailVerificationField(label=_("Email"),
                                error_messages={'required': _('Email is a required field.'),},
                                help_text=_('A receipt will be automatically emailed to the email address provided above.'))
    email_receipt = forms.BooleanField(initial=True, required=False,
                                       help_text=_('A receipt will be automatically emailed to the email address provided above.'))
    comments = forms.CharField(max_length=1000, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    allocation = forms.ChoiceField()
    donate_to_entity_id = forms.ChoiceField()

    class Meta:
        model = Donation
        fields = ('donation_amount',
                  'payment_method',
                  'first_name',
                  'last_name',
                  'company',
                  'address',
                  'address2',
                  'city',
                  'state',
                  'zip_code',
                  'country',
                  'phone',
                  'email',
                  'email_receipt',
                  'allocation',
                  'donate_to_entity_id',
                  'referral_source',
                  'comments',
                  )
        fieldsets = [('', {
                      'fields': ['donation_amount',
                                 'donate_to_entity_id',
                                 'allocation',
                                 'payment_method',
                                 ],
                      'legend': ''
                      }),
                      (_('Billing Information'), {
                      'fields': ['first_name',
                                 'last_name',
                                 'company',
                                  'address',
                                  'address2',
                                  'city',
                                  'state',
                                  'zip_code',
                                  'country',
                                  'phone',
                                  'email',
                                  'email_receipt',
                                 ],
                      }),
                      (_('Other Information'), {
                      'fields': ['referral_source',
                                 'comments',],
                      }),
                     ]

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            self.user = None
        self.hide_amount = False
        super(DonationForm, self).__init__(*args, **kwargs)
        # populate the user fields
        if self.user and self.user.id:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            try:
                profile = self.user.profile
                if profile:
                    self.fields['company'].initial = profile.company
                    self.fields['address'].initial = profile.address
                    self.fields['address2'].initial = profile.address2
                    self.fields['city'].initial = profile.city
                    self.fields['state'].initial = profile.state
                    self.fields['zip_code'].initial = profile.zipcode
                    self.fields['country'].initial = profile.country
                    self.fields['phone'].initial = profile.phone
            except:
                pass
        payment_method_choices = get_payment_method_choices(self.user)
        self.fields['payment_method'] = forms.ChoiceField(choices=payment_method_choices, widget=forms.RadioSelect()) 
        if len(payment_method_choices) == 1:
            self.fields['payment_method'].initial = payment_method_choices[0][0]
            self.fields['payment_method'].widget = forms.HiddenInput()
        # donate_to_entity or allocation
        filters = Entity.get_search_filter(self.user)
        entity_qs = Entity.objects.filter(show_for_donation=True)
        preset_amount_str = (get_setting('module', 'donations', 'donationspresetamounts')).strip('')
        preset_amount_list = preset_amount_str.split(',') if preset_amount_str else None
        if filters:
            entity_qs = entity_qs.filter(filters).distinct()
        if not entity_qs.exists():
            del self.fields['donate_to_entity_id']
            allocation_str = get_setting('module', 'donations', 'donationsallocations')
            if allocation_str:
                self.fields['allocation'].choices = get_allocation_choices(self.user, allocation_str)
            else:
                del self.fields['allocation']
        else:
            del self.fields['allocation']
            if preset_amount_list and get_setting('module', 'donations', 'hide_amount'):
                preset_amount_list = [Decimal(amount) for amount in preset_amount_list]
                self.hide_amount = True
                self.fields['donate_to_entity_id'] = forms.ChoiceField(widget=forms.RadioSelect(), choices=self.get_entity_choices(entity_qs, preset_amount_list))
                self.fields['donate_to_entity_id'].label = _('Contribute to')
                #self.fields['donate_to_entity'].widget = forms.RadioSelect(choices=self.get_entity_choices(entity_qs, preset_amount_list))
            else:
                #self.fields['donate_to_entity_id'].queryset = entity_qs
                self.fields['donate_to_entity_id'].choices = [('', _("Select One"))] + self.get_entity_choices(entity_qs)
                #self.fields['donate_to_entity_id'].empty_label = _("Select One")
                self.fields['donate_to_entity_id'].label = _('Donate to')

        if preset_amount_str:
            self.fields['donation_amount'] = forms.ChoiceField(choices=get_preset_amount_choices(preset_amount_str))
        currency_symbol = get_setting('site', 'global', 'currencysymbol')
        self.fields['donation_amount'].label = _(f'Donation amount ({currency_symbol})')

        # state
        if get_setting('site', 'global', 'stateusesdropdown'):
            self.fields['state'] = StateSelectField(label=self.fields['state'].label,
                                                    required=self.fields['state'].required)
            self.fields['state'].widget.attrs.update({'class': 'form-control'})

        self.fields['email_receipt'].widget = forms.HiddenInput()
        
        # check required fields
        required_fields = get_setting('module', 'donations', 'requiredfields')
        if required_fields:
            required_fields_list = [field.strip() for field in required_fields.split(',') if field.strip()]
            for field_name in required_fields_list:
                if field_name in self.fields:
                    self.fields[field_name].required = True


    def get_entity_choices(self, entity_qs, preset_amount_list=None):
        from django.utils.safestring import mark_safe
        choices_list = []
        for entity in entity_qs:
            if preset_amount_list:
                for amount in preset_amount_list:
                    choices_list.append((entity.id, mark_safe(entity.entity_name + f' <span data-amount="{amount}">{tcurrency(amount)}</span>')))
            else:
                choices_list.append((entity.id, entity.entity_name))
        return choices_list

    def clean_donation_amount(self):
        #raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))
        try:
            if float(self.cleaned_data['donation_amount']) <= 0:
                raise forms.ValidationError(_(u'Please enter a positive number'))
        except:
            raise forms.ValidationError(_(u'Please enter a numeric positive number'))
        return self.cleaned_data['donation_amount']
