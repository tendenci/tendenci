from decimal import Decimal

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.events.addons.utils import can_use_addon

class RegAddonBaseFormSet(BaseFormSet):
    """
    Extending the BaseFormSet to be able to add extra_params.
    note that extra_params does not consider conflicts in a single form's kwargs.
    """
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, **kwargs):
        self.event = kwargs.pop('event')
        self.extra_params = kwargs.pop('extra_params', {})
        super(RegAddonBaseFormSet, self).__init__(data, files, auto_id, prefix,
                 initial, error_class)
        
    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {
            'auto_id': self.auto_id,
            'prefix': self.add_prefix(i),
            'form_index': i,
        }
        
        for key in self.extra_params.keys():
            defaults[key] = self.extra_params[key]
        if self.data or self.files:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        
        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        
        return form
        
    def get_total_price(self):
        total_price = Decimal('0.00')
        for form in self.forms:
            addon = form.chosen_addon
            if addon:
                total_price += addon.price
        return total_price
