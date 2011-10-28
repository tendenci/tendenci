from django import forms
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files import File
from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType

from site_settings.utils import (delete_setting_cache, cache_setting,
    delete_all_settings_cache, get_form_list, get_box_list)
from site_settings.cache import SETTING_PRE_KEY

from tastypie.models import ApiKey
from site_settings.models import Setting
from perms.utils import is_developer

class ApiKeyForm(forms.ModelForm):
    """
    From for setting up ApiKeys for developers.
    """
    
    class Meta:
        model = ApiKey
        exclude = ('created', 'key')
        
    def clean_user(self):
        user = self.cleaned_data['user']
        if not is_developer(user):
            raise forms.ValidationError('This user is not a developer.')
        return user
        
class SettingForm(forms.ModelForm):
    """
    Setting Form made specifically for API validation.
    This is based on the built form of site_settings but instead
    focuses on 1 setting only instead of all the settings of a module.
    """
    class Meta:
        model = Setting
        fields = ('value',)
    
    def __init__(self, *args, **kwargs):
        super(SettingForm, self).__init__(*args, **kwargs)
        setting = self.instance
        if setting:
            if setting.input_type == 'text':
                options = {
                    'label': setting.label,
                    'help_text': setting.description,
                    'initial': setting.value,
                    'required': False
                }
                self.fields['value'] = forms.CharField(**options)
                    
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
                self.fields['value'] = forms.ChoiceField(**options)
            
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
                self.fields['value'] = forms.FileField(**options)
        
    def clean(self):
        """
        Clean method is based on clean_settings_form from site_settings.forms.
        """
        setting = self.instance
        cleaned_data = super(SettingForm, self).clean()
        if setting:
            field_value = cleaned_data['value']
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
        return cleaned_data
