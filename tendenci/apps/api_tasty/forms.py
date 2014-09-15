from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from tastypie.models import ApiKey
from tendenci.core.perms.models import TendenciBaseModel

class ApiKeyForm(forms.ModelForm):
    """
    From for setting up ApiKeys for superusers.
    """

    class Meta:
        model = ApiKey
        exclude = ('created', 'key')

    def clean_user(self):
        user = self.cleaned_data['user']
        if not user.profile.is_superuser:
            raise forms.ValidationError(_('This user is not a superuser.'))
        return user

class TendenciForm(forms.ModelForm):
    """Form that allows owner and creator fields to be editable
    """
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    owner = forms.ModelChoiceField(queryset=User.objects.all())

    class Meta:
        model = TendenciBaseModel
