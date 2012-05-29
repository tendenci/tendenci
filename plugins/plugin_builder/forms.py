import re, os
from django import forms
from django.utils.importlib import import_module
from plugin_builder.models import Plugin, PluginField

class PluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        
    def clean_single_caps(self):
        data = self.cleaned_data['single_caps']
        data = data.strip().replace(' ', '_')
        return data
    
    def clean_plural_caps(self):
        data = self.cleaned_data['plural_caps']
        data = data.strip().replace(' ', '_')
        return data
        
    def clean_single_lower(self):
        data = self.cleaned_data['single_lower']
        data = data.strip().replace(' ', '_').lower()
        if not re.search(r'^[_a-zA-Z]\w*$', data):
            # Provide a smart error message, depending on the error.
            if not re.search(r'^[_a-zA-Z]', data):
                message = 'make sure the name begins with a letter or underscore'
            else:
                message = 'use only numbers, letters and underscores'
            raise forms.ValidationError("%r is not a valid plugin name. Please %s." % (data, message))
        if data == os.path.basename(os.getcwd()):
            raise forms.ValidationError("You cannot create an app with\
                the same name as your project.")
        return data
    
    def clean_plural_lower(self):
        data = self.cleaned_data['plural_lower']
        data = data.strip().replace(' ', '_').lower()
        if not self.instance:
            try:
                import_module(data)
            except ImportError:
                pass
            else:
                raise forms.ValidationError("%r conflicts with the name of an \
                    existing Python module and cannot be used as an app name.\
                    Please try another name." % data)
        return data

class PluginFieldForm(forms.ModelForm):
    class Meta:
        model = PluginField
        
    def clean_name(self):
        data = self.cleaned_data['name']
        data = data.strip().replace(' ', '_').lower()
        if data == 'tags':
            raise forms.ValidationError("This field is already part of the \
                model by default.")                
        return data
        
    def clean(self):
        data = self.cleaned_data
        return data
