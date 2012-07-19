from django import forms

from redirects.models import Redirect

class RedirectForm(forms.ModelForm):
    def clean_from_url(self):
        value = self.cleaned_data['from_url']
        value = value.strip('/')
        return value

    def clean_to_url(self):
        value = self.cleaned_data['to_url']
        value = value.strip('/')
        return value
        
    class Meta:
        model = Redirect

