from django import forms
from django.contrib.auth.models import User
from tastypie.models import ApiKey
from perms.utils import is_developer
from perms.models import TendenciBaseModel

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

class TendenciForm(forms.ModelForm):
    """Form that allows owner and creator fields to be editable
    """
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    owner = forms.ModelChoiceField(queryset=User.objects.all())

    class Meta:
        model = TendenciBaseModel
        
