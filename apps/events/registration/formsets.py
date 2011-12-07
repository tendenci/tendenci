from decimal import Decimal

from django.forms.formsets import BaseFormSet
from django.forms.util import ErrorList

class RegistrantBaseFormSet(BaseFormSet):
    """
    Extending the BaseFormSet to be able to add extra_params.
    note that extra_params does not consider conflicts in a single form's kwargs.
    """
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, **kwargs):
        self.extra_params = kwargs.pop('extra_params', {})
        super(RegistrantBaseFormSet, self).__init__(data, files, auto_id, prefix,
                 initial, error_class)
                 
        # initialize internal variables
        self.pricings = {}
        self.total_price = Decimal('0.00')
        
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
        
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        
        return form
    
    def clean(self):
        """
        Validate the set of registrants for all the pricings used.
        """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        
        # organize the forms based on pricings used
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            pricing = form.cleaned_data['pricing']
            if pricing in self.pricings:
                self.pricings[pricing].append(form)
            else:
                self.pricings[pricing] = [form,]
        
        # validate the reg quantity for each pricing
        for pricing in self.pricings.keys():
            # the registrant length must be divisible by the pricing's quantity
            if len(self.pricings[pricing]) % pricing.quantity != 0:
                raise forms.ValidationError(_("Please enter a valid number of registrants."))
        
        # if all quantities are valid, update each form's corresponding price 
        for pricing in self.pricings.keys():
            for i in range(0, len(self.pricings[pricing])):
                if i % pricing.quantity == 0:
                    price = pricing.price
                else:
                    price = Decimal('0.00')
                
                # associate the price with the form
                form = self.pricings[pricing][i]
                form.set_price(price)
                
                # update the total price
                self.total_price += price
        
    def get_total_price(self):
        return self.total_price
