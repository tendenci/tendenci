from django import forms
from registration.forms import RegistrationForm
from profiles.models import Profile
from registration.models import RegistrationProfile


class RegistrationCustomForm(RegistrationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    company = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':'40'}), required=False)
    phone = forms.CharField(max_length=50, required=False)
    address = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'size':'40'}), required=False)
    city = forms.CharField(max_length=50, required=False)
    state = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'size':'10'}), required=False)
    country = forms.CharField(max_length=50, required=False)
    zipcode = forms.CharField(max_length=50, required=False)
    
    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'])
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        
        new_profile = Profile(user=new_user, 
                              company=self.cleaned_data['company'],
                              phone=self.cleaned_data['phone'],
                              address=self.cleaned_data['address'],
                              city=self.cleaned_data['city'],
                              state=self.cleaned_data['state'],
                              country=self.cleaned_data['country'],
                              zipcode=self.cleaned_data['zipcode'],
                              )
        new_profile.creator = new_user
        new_profile.creator_username = new_user.username
        new_profile.owner = new_user
        new_profile.owner_username = new_user.username
        new_profile.save()
        
        return new_user