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
        """
        Builds the field for the setting's value based on the setting's
        properties.
        """
        self.request = kwargs.pop('request', None)
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
                options = {
                    'label': setting.label,
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
                    # save a file object and set the value at that file object's id.
                    from files.models import File as TendenciFile
                    uploaded_file = TendenciFile()
                    uploaded_file.owner = self.request.user
                    uploaded_file.owner_username = self.request.user.username
                    uploaded_file.creator = self.request.user
                    uploaded_file.creator_username = self.request.user.username
                    uploaded_file.content_type = ContentType.objects.get(app_label="site_settings", model="setting")
                    uploaded_file.file.save(field_value.name, File(field_value))
                    uploaded_file.save()
                    field_value = uploaded_file.pk
                else:
                    #retain the old file if no file is set
                    field_value = setting.value
        return cleaned_data
