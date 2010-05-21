from django import forms
from django.utils.translation import ugettext_lazy as _


import logging

def clean_settings_form(self):
    logging.debug(self.cleaned_data)
    
def build_settings_form(settings):
    """
        Create a set of fields and builds a form class
        returns SettingForm
    """
    fields = {}
    for setting in settings:
        if setting.input_type == 'text':
            options = {
                'label': setting.label,
                'help_text': setting.description,
                'initial': setting.value,
                'required': False
            }
            fields.update({"%s" % setting.name : forms.CharField(**options) })
        if setting.input_type == 'select':
            options = {
                'label': setting.label,
                'help_text': setting.description,
                'initial': setting.value,
                'choices': tuple([(s,s)for s in setting.input_value.split(',')])
            }
            fields.update({"%s" % setting.name : forms.ChoiceField(**options) }) 
            
    return type('SettingForm', (forms.BaseForm,), { 'base_fields': fields, 'clean': clean_settings_form })
