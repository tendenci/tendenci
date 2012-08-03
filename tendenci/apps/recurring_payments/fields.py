from django import forms
from django.utils.safestring import mark_safe

from widgets import BillingCycleWidget

from tendenci.core.site_settings.utils import get_setting

    
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
        
class PriceInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        currency_symbol = get_setting('site', 'global', 'currencysymbol')
        if currency_symbol == '': currency_symbol = "$"
        return mark_safe('$ %s' % super(PriceInput, self).render(name, value, attrs))