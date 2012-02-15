from django import forms
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files import File
from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType

from tastypie.models import ApiKey

from perms.utils import is_developer
from site_settings.utils import get_form_list, get_box_list
from site_settings.models import Setting
from profiles.models import Profile

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
        
class UserForm(forms.ModelForm):
    """UserForm for API validation
    """
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        )
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserForm, self).__init__(*args, **kwargs)
        
class ProfileForm(forms.ModelForm):
    """Profile Form
    """
    class Meta:
        model = Profile
        fields = (
            'salutation',
            'user',
            'phone',
            'phone2',
            'fax',
            'work_phone',
            'home_phone',
            'mobile_phone',
            'email',
            'email2',
            'company',
            'position_title',
            'position_assignment',
            'display_name',
            'hide_in_search',
            'hide_phone',
            'hide_email',
            'hide_address',
            'initials',
            'sex',
            'mailing_name',
            'address',
            'address2',
            'city',
            'state',
            'zipcode',
            'county',
            'country',
            'url',
            'dob',
            'ssn',
            'spouse',
            'time_zone',
            'department',
            'education',
            'student',
            'direct_mail',
            'notes',
            'allow_anonymous_view',
            'admin_notes',
            'entity',
            'status',
            'status_detail',
        )
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        
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
        Clean method is based on clean_settings_form from site_settings.forms.
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
                    raise forms.ValidationError("'%s' must be true or false" % setting.label)
            if setting.data_type == "int":
                if field_value != ' ':
                    if not field_value.isdigit():
                        raise forms.ValidationError("'%s' must be a whole number" % setting.label)
            if setting.data_type == "file":
                #API can't support file uploads without a workaround to another view.
                if field_value:
                    #file fields will be considered as id fields for Files
                    if not field_value.isdigit():
                        raise forms.ValidationError("'%s' must be a File pk" % setting.label)
                    
                    #if the value is an int use it as pk to get a File
                    from files.models import File as TendenciFile
                    try:
                        tfile = TendenciFile.objects.get(pk=field_value)
                    except TendenciFile.DoesNotExist:
                        raise forms.ValidationError("File entry does not exist.")
                    
        return cleaned_data

