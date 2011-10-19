from ordereddict import OrderedDict

from django import forms
from django.core.cache import cache

from site_settings.utils import (delete_setting_cache, cache_setting,
    delete_all_settings_cache, get_form_list, get_box_list)
from site_settings.cache import SETTING_PRE_KEY

def clean_settings_form(self):
    """
        Cleans data that has been set in the settings form
    """
    for setting in self.settings:
        try:
            field_value = self.cleaned_data[setting.name]
            if setting.data_type == "boolean":
                if field_value != 'true' and field_value != 'false':
                    raise forms.ValidationError("'%s' must be true or false" % setting.label)
            if setting.data_type == "int":
                if field_value != ' ':
                    if not field_value.isdigit():
                        raise forms.ValidationError("'%s' must a whole number" % setting.label)
        except KeyError:
            pass
    return self.cleaned_data

    
def save_settings_form(self):
    """
        Save the updated settings in the database 
        Removes and updates the settings cache
    """
    for setting in self.settings:
        try:
            field_value = self.cleaned_data[setting.name]
            if setting.value != field_value:
                # delete the cache for all the settings to reset the context
                key = [SETTING_PRE_KEY, 'all.settings']
                key = '.'.join(key)
                cache.delete(key)
                
                # delete and set cache for single key and save the value in the database
                delete_all_settings_cache()
                delete_setting_cache(setting.scope, setting.scope_category, setting.name)
                setting.value = field_value
                setting.save()
                cache_setting(setting.scope, setting.scope_category, setting.name,
                  setting)
        except KeyError:
            pass
            

def build_settings_form(user, settings):
    """
        Create a set of fields and builds a form class
        returns SettingForm class
    """
    fields = OrderedDict()
    for setting in settings:
        if setting.input_type == 'text':
            options = {
                'label': setting.label,
                'help_text': setting.description,
                'initial': setting.value,
                'required': False
            }
            if setting.client_editable:
                fields.update({"%s" % setting.name : forms.CharField(**options) })
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name : forms.CharField(**options) })
                    
        if setting.input_type == 'select':
            if setting.input_value == '<form_list>':
                choices = get_form_list(user)
            elif setting.input_value == '<box_list>':
                choices = get_box_list(user)
            else:
                choices = tuple([(s,s)for s in setting.input_value.split(',')])
            options = {
                'label': setting.label,
                'help_text': setting.description,
                'initial': setting.value,
                'choices': choices,
            }
            if setting.client_editable:
                fields.update({"%s" % setting.name : forms.ChoiceField(**options) }) 
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name : forms.ChoiceField(**options) })
                
       
    attributes = {
        'settings': settings,
        'base_fields': fields,
        'clean': clean_settings_form,
        'save': save_settings_form,
    }     
    return type('SettingForm', (forms.BaseForm,), attributes)
