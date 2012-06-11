from django import forms
from pluginmanager.models import PluginApp

class PluginAppForm(forms.ModelForm):
    class Meta:
        model = PluginApp
    
    def clean_package(self):
        package = self.cleaned_data['package']
        package = package.strip().replace(' ', '_')
        return package
