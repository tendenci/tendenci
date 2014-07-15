from django import forms
from django.utils.safestring import mark_safe

from tendenci.addons.recurring_payments.widgets import BillingCycleWidget


class BillingCycleField(forms.MultiValueField):
    def __init__(self, required=True, widget=BillingCycleWidget(attrs=None),
                label=None, initial=None, help_text=None):
        myfields = ()
        super(BillingCycleField, self).__init__(myfields, required, widget,
                                          label, initial, help_text)

    def clean(self, value):
        return self.compress(value)

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None
