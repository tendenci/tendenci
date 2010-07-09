import datetime
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
from profiles.models import Profile
from perms.forms import TendenciBaseForm
from perms.utils import is_admin, is_developer

attrs_dict = {'class': 'required' }
THIS_YEAR = datetime.date.today().year
# this is the list of apps whose permissions will be displayed on the permission edit page
APPS = ['profiles', 'user_groups', 'articles', 
        'news', 'pages', 'jobs', 'locations', 
        'stories', 'actions']

class ProfileForm(TendenciBaseForm):
    first_name = forms.CharField(label=_("First Name"), max_length=100,
                                 error_messages={'required': 'First Name is a required field.'})
    last_name = forms.CharField(label=_("Last Name"), max_length=100,
                                error_messages={'required': 'Last Name is a required field.'})
    email = forms.CharField(label=_("Email"), max_length=100,
                                 error_messages={'required': 'Email is a required field.'})
    initials = forms.CharField(label=_("Initial"), max_length=100, required=False,
                               widget=forms.TextInput(attrs={'size':'10'}))
    display_name = forms.CharField(label=_("Display name"), max_length=100, required=False,
                               widget=forms.TextInput(attrs={'size':'30'}))
    
    url = forms.CharField(label=_("Web Site"), max_length=100, required=False,
                               widget=forms.TextInput(attrs={'size':'40'}))
    company = forms.CharField(label=_("Company"), max_length=100, required=False,
                              error_messages={'required': 'Company is a required field.'},
                               widget=forms.TextInput(attrs={'size':'45'}))
    department = forms.CharField(label=_("Department"), max_length=100, required=False,
                               widget=forms.TextInput(attrs={'size':'35'}))
    address = forms.CharField(label=_("Address"), max_length=150, required=False,
                              error_messages={'required': 'Address is a required field.'},
                               widget=forms.TextInput(attrs={'size':'45'}))
    address2 = forms.CharField(label=_("Address2"), max_length=100, required=False,
                               widget=forms.TextInput(attrs={'size':'40'}))
    city = forms.CharField(label=_("City"), max_length=50, required=False,
                           error_messages={'required': 'City is a required field.'},
                               widget=forms.TextInput(attrs={'size':'15'}))
    state = forms.CharField(label=_("State"), max_length=50, required=False,
                            error_messages={'required': 'State is a required field.'},
                               widget=forms.TextInput(attrs={'size':'5'}))
    zipcode = forms.CharField(label=_("Zipcode"), max_length=50, required=False,
                              error_messages={'required': 'Zipcode is a required field.'},
                               widget=forms.TextInput(attrs={'size':'10'}))
    country = forms.CharField(label=_("Country"), max_length=50, required=False,
                              error_messages={'required': 'Country is a required field.'},
                               widget=forms.TextInput(attrs={'size':'15'}))
    mailing_name = forms.CharField(label=_("Mailing Name"), max_length=120, required=False,
                                   error_messages={'required': 'Mailing name is a required field.'},
                               widget=forms.TextInput(attrs={'size':'30'}))
    
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
    interactive = forms.ChoiceField(initial=1, choices=((1,'Interactive'),
                                                          (0,'Not Interactive (no login)'),))
    direct_mail =  forms.ChoiceField(initial=1, choices=((1, 'Yes'),(0, 'No'),))
    notes = forms.CharField(label=_("Notes"), max_length=1000, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    admin_notes = forms.CharField(label=_("Admin Notes"), max_length=1000, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    language = forms.ChoiceField(initial="en-us", choices=(('en-us', u'English'),))
    dob = forms.DateField(required=False, widget=SelectDateWidget(None, range(THIS_YEAR-100, THIS_YEAR)))
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
                  'interactive', 
                  'status', 
                  'status_detail',
                  'allow_anonymous_view',
                  'admin_notes',
                  'entity',
                  'security_level',
                
                )
        
    def __init__(self, user_current=None, user_this=None, required_fields_list=None, *args, **kwargs):
        super(ProfileForm, self).__init__(user_current, *args, **kwargs)
        self.user_this = user_this
        
        self.fields['user_perms'].label = "Owner"
        self.fields['user_perms'].help_text = "People who can edit this user"
        
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
            if user_this.is_active == 1:
                self.fields['interactive'].initial = 1
            else:
                self.fields['interactive'].initial = 0
                
            del self.fields['password1']
            del self.fields['password2']
            
            if not is_admin(user_current):
                del self.fields['admin_notes']
                del self.fields['security_level']
                del self.fields['status']
                del self.fields['status_detail']
            if is_admin(user_current) and not is_developer(user_current):
                self.fields['security_level'].choices=(('user','User'),
                                                            ('admin','Admin'),)
        # we make first_name, last_name, email, username and password as required field regardless
        # the rest of fields will be decided by the setting - UsersRequiredFields
        if required_fields_list:
            for field in required_fields_list:
                for myfield in self.fields:
                    if field == self.fields[myfield].label:
                        self.fields[myfield].required = True
                        continue
            
        
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
            if self.user_this and user.id==self.user_this.id and user.username==self.user_this.username:
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
           
            new_user.save()
            self.instance.user = new_user
            
            # if not self.instance.owner:
            self.instance.owner = request.user
        else:
            user_edit.username = username
            user_edit.email = email
            user_edit.first_name = self.cleaned_data['first_name']
            user_edit.last_name = self.cleaned_data['last_name']
            
            user_edit.save()
            
        if not self.instance.id:
            self.instance.creator = request.user
            self.instance.creator_username = request.user.username
        self.instance.owner = request.user
        self.instance.owner_username = request.user.username
            
        return super(ProfileForm, self).save(*args, **kwargs)
    
        
class UserForm(forms.ModelForm):
    is_superuser = forms.BooleanField(label=_("Is Admin"), 
                                      help_text = _("If selected, this user has all permissions without explicitly assigning them."))
    class Meta:
        model = User
        fields= ('is_superuser', 'user_permissions')
        
class UserPermissionForm(forms.ModelForm):
    is_superuser = forms.BooleanField(label=_("Is Admin"), 
                                      help_text = _("If selected, admin has all permissions without explicitly assigning them."))
    class Meta:
        model = User
        fields= ('is_superuser', 'user_permissions',)
        
    def __init__(self, *args, **kwargs):
        super(UserPermissionForm, self).__init__(*args, **kwargs)
        # filter out the unwanted permissions,
        # only display the permissions for the apps in APPS
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission
        content_types = ContentType.objects.filter(app_label__in=APPS)
        
        self.fields['user_permissions'].queryset = Permission.objects.filter(content_type__in=content_types)
    
        
