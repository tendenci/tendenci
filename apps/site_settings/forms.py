from ordereddict import OrderedDict

from django import forms
from django.core.cache import cache
from django.core.files import File
from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType

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
                        raise forms.ValidationError("'%s' must be a whole number" % setting.label)
            if setting.data_type == "file":
                if field_value:
                    if not isinstance(field_value, File):
                        raise forms.ValidationError("'%s' must be a file" % setting.label)
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
            
            if setting.input_type == "file":
                if field_value:
                    # save a file object and set the value at that file object's id.
                    from files.models import File as TendenciFile
                    uploaded_file = TendenciFile()
                    uploaded_file.owner = self.user
                    uploaded_file.owner_username = self.user.username
                    uploaded_file.creator = self.user
                    uploaded_file.creator_username = self.user.username
                    uploaded_file.content_type = ContentType.objects.get(app_label="site_settings", model="setting")
                    uploaded_file.file.save(field_value.name, File(field_value))
                    uploaded_file.save()
                    field_value = uploaded_file.pk
                else:
                    #retain the old file if no file is set
                    field_value = setting.value
                    
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
                    
        elif setting.input_type == 'select':
            if setting.input_value == '<form_list>':
                choices = get_form_list(user)
                required = False
            elif setting.input_value == '<box_list>':
                choices = get_box_list(user)
                required = False
            else:
                choices = tuple([(s,s)for s in setting.input_value.split(',')])
                required = True
            options = {
                'label': setting.label,
                'help_text': setting.description,
                'initial': setting.value,
                'choices': choices,
                'required': required,
            }
            if setting.client_editable:
                fields.update({"%s" % setting.name : forms.ChoiceField(**options) }) 
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name : forms.ChoiceField(**options) })
            
        elif setting.input_type == 'file':
            from files.models import File as TendenciFile
            try:
                try: val = int(setting.value)
                except: val = 0
                
                tfile = TendenciFile.objects.get(pk=val)
                if tfile.file.name.lower().endswith(('.jpg', '.jpe', '.png', '.gif', '.svg')):
                    file_display = '<img src="/files/%s/80x80/crop/">' % tfile.pk
                else:
                    file_display = tfile.file.name
            except TendenciFile.DoesNotExist:
                file_display = "No file"
            options = {
                'label': setting.label,
                'help_text': "%s<br> Current File: %s" % (setting.description, file_display),
                'initial': tfile.file,
                'required': False
            }
            if setting.client_editable:
                fields.update({"%s" % setting.name : forms.FileField(**options) })
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name : forms.FileField(**options) })
       
    attributes = {
        'settings': settings,
        'base_fields': fields,
        'clean': clean_settings_form,
        'save': save_settings_form,
        'user': user,
    }     
    return type('SettingForm', (forms.BaseForm,), attributes)
