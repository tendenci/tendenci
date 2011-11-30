from django import forms

from events.models import RegConfPricing
from events.utils import get_available_pricings

class PricingForm(forms.Form):
    """
    This form is the user's pricing selection.
    This form will be mainly used for ajax requests.
    This is the first form a user must answer before a registrant formset is loaded.
    """
    
    pricing = forms.ModelChoiceField(queryset=RegConfPricing.objects.none())
    
    def __init__(self, user, event, *args, **kwargs):
        super(PricingForm, self).__init__(*args, **kwargs)
        
        #initialize pricing options
        pricings = get_available_pricings(event, user)
        self.field['pricing'].queryset = pricings


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

class RegistrantForm(forms.Form):
    """
    Each registrant form will have a hidden pricing field.
    Each registrant form will have a hidden reg_set field.
    The reg_set field will be used to group the registrant data and validate
    them as a whole.
    """
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    company_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)
    
    def __init__(self, *args, **kwargs):
        self.pricings = kwargs.pop('pricings')
        self.form_index = kwargs.pop('form_index', None)
        
        super(RegistrantForm, self).__init__(*args, **kwargs)
        
        # make the fields in the subsequent forms as not required
        if self.form_index and self.form_index > 0:
            for key in self.fields.keys():
                self.fields[key].required = False
                
        #initialize pricing options and reg_set field
        self.fields['pricing'] = forms.ModelChoiceField(widget=forms.HiddentInput, queryset=pricings)
        self.fields['reg_set'] = forms.IntegerField(widget=forms.HiddenInput)
    
    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        
        # detect markup
        markup_pattern = re.compile('<[^>]*?>', re.I and re.M)
        markup = markup_pattern.search(data)
        if markup:
            raise forms.ValidationError("Markup is not allowed in the name field")

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError("URL's and Emails are not allowed in the name field")
        
        data.strip()
        return data
        
    def clean_last_name(self):
        data = self.cleaned_data['first_name']
        
        # detect markup
        markup_pattern = re.compile('<[^>]*?>', re.I and re.M)
        markup = markup_pattern.search(data)
        if markup:
            raise forms.ValidationError("Markup is not allowed in the name field")

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError("URL's and Emails are not allowed in the name field")
        
        data.strip()
        return data
    
    def clean_email(self):
        data = self.cleaned_data['email']
        data.strip()
        return data
