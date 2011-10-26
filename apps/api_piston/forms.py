from django import forms

from site_settings.models import Setting

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
            elif setting.input_type == 'file':
                from files.models import File as TendenciFile
                try:
                    tfile = TendenciFile.objects.get(pk=setting.value)
                    if tfile.file.name.lower().endswith(('.jpg', '.jpe', '.png', '.gif', '.svg')):
                        file_display = '<img src="/files/%s/80x80/crop/">' % tfile.pk
                    else:
                        file_display = tfile.file.name
                except TendenciFile.DoesNotExist:
                    file_display = "No file"
                options = {
                    'label': setting.label,
                    'help_text': "%s<br> Current File: %s" % (setting.description, file_display),
                    'initial': setting.value,
                    'required': False
                }
            else:
                options = {
                    'label': setting.label,
                    'help_text': setting.description,
                    'initial': setting.value,
                    'required': False
                }
            
            self.fields['value'] = forms.CharField(**options)
        
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
                if not isinstance(field_value, File):
                    raise forms.ValidationError("'%s' must be a file" % setting.label)
            
