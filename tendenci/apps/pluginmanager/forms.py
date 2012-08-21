from django import forms
from tendenci.apps.pluginmanager.models import PluginApp
from tendenci.apps.pluginmanager.utils import plugin_options


class PluginAppForm(forms.ModelForm):
    package = forms.ChoiceField(widget=forms.Select(), label="App Name")

    class Meta:
        model = PluginApp
        fields = (
            'package',
            'description',
            'is_enabled',
        )

    def __init__(self, *args, **kwargs):
        super(PluginAppForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['package'].choices = ((self.instance.package, self.instance.title),)
        else:
            self.fields['package'].choices = plugin_options()

    def clean_package(self):
        package = self.cleaned_data['package']
        package = package.strip().replace(' ', '_')

        try:
            __import__(package)
        except:
            raise forms.ValidationError('This plugin does not exist. Please add the name of a valid plugin.')

        return package
