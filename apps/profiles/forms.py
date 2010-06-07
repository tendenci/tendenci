from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from profiles.models import Profile

attrs_dict = {'class': 'required' }

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First Name"), max_length=100)
    last_name = forms.CharField(label=_("Last Name"), max_length=100)
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'Username'))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs=attrs_dict))
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(attrs=attrs_dict),
        help_text = _("Enter the same password as above, for verification."))
    security_level = forms.ChoiceField(initial="user", choices=(('user','User'),
                                                                ('admin','Admin'),
                                                                ('developer','Developer'),))
    class Meta:
        model = Profile
        fields = ('salutation', 
                  'first_name',
                  'last_name',
                  'username',
                  'password1',
                  'password2',
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
                  'sex',
                  'address',
                  'address2',
                  'city',
                  'state',
                  'zipcode',
                  'county',
                  'country',
                  'url',
                  'url2',
                  'dob',
                  'ssn',
                  'spouse',
                  'department',
                  'education',
                  'student',
                  'direct_mail',
                  'notes',
                  'allow_anonymous_view',
                  'admin_notes',
                  'security_level',
                  'status', 
                  'status_detail',
                
                )
        
    def __init__(self, user_this, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.user_this = user_this
        
        if user_this:
            self.fields['first_name'].initial = user_this.first_name
            self.fields['last_name'].initial = user_this.last_name
            self.fields['username'].initial = user_this.username
            if user_this.is_superuser and user_this.is_staff:
                self.fields['security_level'].initial = "developer"
            elif user_this.is_superuser:
                self.fields['security_level'].initial = "admin"
            else:
                self.fields['security_level'].initial = "user"
            del self.fields['password1']
            del self.fields['password2']
            #if not user_current.is_superuser:
            #    del self.fields['admin_notes']
            #    del self.fields['security_level']
            #    del self.fields['status']
            #    del self.fields['status_detail']
        
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
            if user==self.user_this:
                return self.cleaned_data['username']
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))
    
    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if not self.user_this:
            if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError(_(u'You must type the same password each time'))
        return self.cleaned_data
        
    def save(self, request, user_edit, *args, **kwargs):
        """
        Create a new user then create the user profile
        """
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        if not self.user_this:
            password = self.cleaned_data['password1']
            new_user = User.objects.create_user(username, email, password)
            new_user.first_name = self.cleaned_data['first_name']
            new_user.last_name = self.cleaned_data['last_name']
            new_user.is_active = self.cleaned_data['status']
            #new_user.is_superuser = self.cleaned_data['is_superuser']
            new_user.save()
            self.instance.user = new_user
            
           # if not self.instance.owner:
            self.instance.owner = request.user
        else:
            user_edit.email = self.cleaned_data['email']
            user_edit.is_active = self.cleaned_data['status']
            #new_user.is_superuser = self.cleaned_data['is_superuser']
            user_edit.save()
            
        if not self.instance.id:
            self.instance.creator = request.user
            
        return super(ProfileForm, self).save(*args, **kwargs)
    
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('salutation',
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
                  'sex',
                  'address',
                  'address2',
                  'city',
                  'state',
                  'zipcode',
                  'county',
                  'country',
                  'url',
                  'url2',
                  'dob',
                  'ssn',
                  'spouse',
                  'department',
                  'education',
                  'student',
                  'direct_mail',
                  'notes',
                  'allow_anonymous_view',
                  'admin_notes',
                  'status', 
                  'status_detail', 
                  'owner',
                )
        
    def save(self, request, user_edit, *args, **kwargs):
        user_edit.email = self.cleaned_data['email']
        user_edit.is_active = self.cleaned_data['status']
        #new_user.is_superuser = self.cleaned_data['is_superuser']
        user_edit.save()
        
        return super(ProfileEditForm, self).save(*args, **kwargs)
    
        
class UserForm(forms.ModelForm):
    is_superuser = forms.BooleanField(label=_("Is Admin"), 
                                      help_text = _("If selected, this user has all permissions without explicitly assigning them."))
    class Meta:
        model = User
        fields= ('is_superuser', 'user_permissions')
        
class UserEditForm(forms.ModelForm):
    is_superuser = forms.BooleanField(label=_("Is Admin"), 
                                      help_text = _("If selected, this user has all permissions without explicitly assigning them."))
    class Meta:
        model = User
        fields= ('first_name', 'last_name', 'is_superuser',)
        
class UserPermissionForm(forms.ModelForm):
    class Meta:
        model = User
        fields= ('is_superuser', 'user_permissions',)
        
