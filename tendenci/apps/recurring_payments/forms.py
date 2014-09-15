from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from tendenci.core.base.fields import PriceField
from tendenci.addons.recurring_payments.models import RecurringPayment
from tendenci.addons.recurring_payments.widgets import BillingCycleWidget, BillingDateSelectInput, BillingDateSelectWidget
from tendenci.addons.recurring_payments.fields import BillingCycleField

class RecurringPaymentForm(forms.ModelForm):
    #status_detail = forms.ChoiceField(choices=(('inactive','Inactive'),('active','Active')),
    #                                  initial='active')
    payment_amount = PriceField(decimal_places=2)
    trial_amount = PriceField(decimal_places=2, required=False)

    billing_dt_select = BillingCycleField(label=_('When to bill'),
                                          widget=BillingDateSelectWidget,
                                          help_text=_('It is used to determine the payment due date for each billing cycle'))
    billing_cycle = BillingCycleField(label=_('How often to bill'),
                                          widget=BillingCycleWidget)

    class Meta:
        model = RecurringPayment
        fields = ('user',
                  'url',
                  'description',
                  'payment_amount',
                  'taxable',
                  'tax_rate',
                  'billing_start_dt',
                  'billing_cycle',
                  'billing_dt_select',
                  'has_trial_period',
                  'trial_period_start_dt',
                  'trial_period_end_dt',
                  'trial_amount',
                  'status',
                  'status_detail',
                  )

    def __init__(self, *args, **kwargs):
        super(RecurringPaymentForm, self).__init__(*args, **kwargs)

        # billing_cycle
        if self.instance.pk:
            initial_list= [str(self.instance.billing_frequency),
                           str(self.instance.billing_period)]
        else:
            initial_list= ['1', 'month']

        self.fields['billing_cycle'].initial = initial_list

        # billing_dt_select
        if self.instance.pk:
            initial_list= [str(self.instance.num_days),
                           str(self.instance.due_sore)]
        else:
            initial_list= ['0', 'start']

        self.fields['billing_dt_select'].initial = initial_list

        self.fields['user'].choices = [(u.id, '%s %s (%s) - %s' % (
                        u.first_name, u.last_name, u.username, u.email
                        )) for u in User.objects.filter(is_active=1).order_by('first_name', 'last_name')]
        self.fields['user'].help_text = """If not found in the list,
                                        <a href="%s">create a new user</a> before proceeding
                                        """ % reverse('profile.add')


    def clean_billing_cycle(self):
        value = self.cleaned_data['billing_cycle']

        data_list = value.split(',')
        d = dict(zip(['billing_frequency', 'billing_period'], data_list))

        try:
            d['billing_frequency'] = int(d['billing_frequency'])
        except:
            raise forms.ValidationError(_("Billing frequency must be a numeric number."))
        return value

    def clean_billing_dt_select(self):
        value = self.cleaned_data['billing_dt_select']

        data_list = value.split(',')
        d = dict(zip(['num_days', 'due_sore'], data_list))

        try:
            d['num_days'] = int(d['num_days'])
        except:
            raise forms.ValidationError(_("Number day(s) must be a numeric number."))
        return value

    def clean_tax_rate(self):
        value = self.cleaned_data['tax_rate']
        taxable = self.cleaned_data['taxable']
        if taxable:
            if not value:
                raise forms.ValidationError(_("Please specify a tax rate."))
            if value > 1:
                raise forms.ValidationError(_("Tax rate should be less than 1."))

        return value
