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
        
