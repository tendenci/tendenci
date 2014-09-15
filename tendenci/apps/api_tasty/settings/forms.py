from django import forms
from tendenci.apps.site_settings.models import Setting
from django.utils.translation import ugettext_lazy as _

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
            if setting.input_type == 'select':
                if setting.input_value == '<form_list>':
                    choices = get_form_list(self.request.user)
                    required = False
                elif setting.input_value == '<box_list>':
                    choices = get_box_list(self.request.user)
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
        Clean method is based on clean_settings_form from tendenci.apps.site_settings.forms.
        """
        setting = self.instance
        cleaned_data = super(SettingForm, self).clean()
        if setting:
            try:
                field_value = cleaned_data['value']
            except KeyError:
                field_value = None

            if setting.data_type == "boolean":
                if field_value != 'true' and field_value != 'false':
                    raise forms.ValidationError(_("'%(label)s' must be true or false" % {'label': setting.label}))
            if setting.data_type == "int":
                if field_value != ' ':
                    if not field_value.isdigit():
                        raise forms.ValidationError(_("'%(label)s' must be a whole number" % {'label':setting.label}))
            if setting.data_type == "file":
                #API can't support file uploads without a workaround to another view.
                if field_value:
                    #file fields will be considered as id fields for Files
                    if not field_value.isdigit():
                        raise forms.ValidationError(_("'%(label)s' must be a File pk" % {'label':setting.label}))

                    #if the value is an int use it as pk to get a File
                    from tendenci.apps.files.models import File as TendenciFile
                    try:
                        tfile = TendenciFile.objects.get(pk=field_value)
                    except TendenciFile.DoesNotExist:
                        raise forms.ValidationError(_("File entry does not exist."))

        return cleaned_data
