from django import forms
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from profiles.models import Profile
from registration.models import RegistrationProfile


class RegistrationCustomForm(RegistrationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    company = forms.CharField()
    
    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'])
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        
        new_profile = Profile(user=new_user, company=self.cleaned_data['company'])
        new_profile.creator = new_user
        new_profile.creator_username = new_user.username
        new_profile.owner = new_user
        new_profile.owner_username = new_user.username
        new_profile.save()
        
        return new_user