from django import forms
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _, ugettext
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
                              email=self.cleaned_data['email'],
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
    
    
class LoginForm(forms.Form):

    username = forms.CharField(label=_("Username"), max_length=30, widget=forms.TextInput())
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    #remember = forms.BooleanField(label=_("Remember Me"), help_text=_("If checked you will stay logged in for 3 weeks"), required=False)
    remember = forms.BooleanField(label=_("Remember Login"), required=False)

    user = None

    def clean(self):
        if self._errors:
            return
        user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        
        if user:
            try:
                profile = user.get_profile()
            except Profile.DoesNotExist:
                profile = Profile.objects.create_profile(user=user)
           
            if user.is_active and profile.status==1 and profile.status_detail.lower()=='active':
                self.user = user
            else:
                raise forms.ValidationError(_("This account is currently inactive."))
        else:
            raise forms.ValidationError(_("The username and/or password you specified are not correct."))
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            login(request, self.user)
            request.user.message_set.create(message=ugettext(u"Successfully logged in as %(username)s.") % {'username': self.user.username})
            if self.cleaned_data['remember']:
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                request.session.set_expiry(0)
                
            return True
        return False