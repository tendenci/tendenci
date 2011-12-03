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
