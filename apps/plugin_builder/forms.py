import re, os
from django import forms
from plugin_builder.models import Plugin

class PluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        
    def clean_single_lower(self):
        data = self.cleaned_data['single_lower']
        if re.search(r'^[_a-zA-Z]\w*$', data):
            # If it's not a valid directory name.
            raise forms.ValidationError("This is not a valid directory name.")
        if data == os.path.basename(os.getcwd()):
            raise forms.ValdidationError("You cannot create an app with\
                the same name as your project.")
        try:
            import_module(app_low_single)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an \
                existing Python module and cannot be used as an app name.\
                Please try another name." % data)
        return data
