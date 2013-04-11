import datetime
import re

from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
from django.utils.safestring import mark_safe

from tendenci.core.base.fields import SplitDateTimeField
from tendenci.core.base.fields import EmailVerificationField
from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.core.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.addons.memberships.models import App, Membership
from tendenci.core.event_logs.models import EventLog
from tendenci.apps.profiles.models import Profile
from tendenci.apps.profiles.utils import get_groups, get_memberships, group_choices, update_user

attrs_dict = {'class': 'required' }
THIS_YEAR = datetime.date.today().year
# this is the list of apps whose permissions will be displayed on the permission edit page
APPS = ('profiles', 'user_groups', 'articles', 
        'news', 'pages', 'jobs', 'locations', 
        'stories', 'actions', 'photos', 'entities',
        'locations', 'files', 'directories', 'resumes',
        'memberships', 'corporate_memberships')

class ProfileForm(TendenciBaseForm):

    first_name = forms.CharField(label=_("First Name"), max_length=100,
                                 error_messages={'required': 'First Name is a required field.'})
    last_name = forms.CharField(label=_("Last Name"), max_length=100,
                                error_messages={'required': 'Last Name is a required field.'})
    email = EmailVerificationField(label=_("Email"),
                                error_messages={'required': 'Email is a required field.'})
    email2 = EmailVerificationField(label=_("Email 2"), required=False)

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
    
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'Username'),
                                help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs=attrs_dict))
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(attrs=attrs_dict),
        help_text = _("Enter the same password as above, for verification."))
    security_level = forms.ChoiceField(initial="user", choices=(('user','User'),
                                                                ('staff','Staff'),
                                                                ('superuser','Superuser'),))
    interactive = forms.ChoiceField(initial=1, choices=((1,'Interactive'),
                                                          (0,'Not Interactive (no login)'),))
    direct_mail =  forms.ChoiceField(initial=1, choices=((1, 'Yes'),(0, 'No'),))
    notes = forms.CharField(label=_("Notes"), max_length=1000, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    admin_notes = forms.CharField(label=_("Admin Notes"), max_length=1000, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    language = forms.ChoiceField(initial="en-us", choices=(('en-us', u'English'),))
    dob = forms.DateField(required=False, widget=SelectDateWidget(None, range(THIS_YEAR-100, THIS_YEAR)))

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

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
                  'allow_anonymous_view',
                  'admin_notes',
                  'security_level',
                  'status',
                  'status_detail',
                )
        
    def __init__(self, *args, **kwargs):
        if 'user_this' in kwargs:
            self.user_this = kwargs.pop('user_this', None)
        else:
            self.user_this = None
            
        if 'user_current' in kwargs:
            self.user_current = kwargs.pop('user_current', None)
        else:
            self.user_current = None            

        if 'required_fields_list' in kwargs:
            self.required_fields_list = kwargs.pop('required_fields_list', None)
        else:
            self.required_fields_list = None      
                        
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        if self.user_this:
            self.fields['first_name'].initial = self.user_this.first_name
            self.fields['last_name'].initial = self.user_this.last_name
            self.fields['username'].initial = self.user_this.username
            self.fields['email'].initial = self.user_this.email

            if self.user_this.is_superuser:
                self.fields['security_level'].initial = "superuser"
            elif self.user_this.is_staff:
                self.fields['security_level'].initial = "staff"
            else:
                self.fields['security_level'].initial = "user"
            if self.user_this.is_active == 1:
                self.fields['interactive'].initial = 1
            else:
                self.fields['interactive'].initial = 0
                
            del self.fields['password1']
            del self.fields['password2']
            
            if not self.user_current.profile.is_superuser:
                del self.fields['admin_notes']
                del self.fields['security_level']
                del self.fields['status']
                del self.fields['status_detail']

            if self.user_current.profile.is_superuser and self.user_current == self.user_this:
                self.fields['security_level'].choices = (('superuser','Superuser'),)

        if not self.user_current.profile.is_superuser:
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        # we make first_name, last_name, email, username and password as required field regardless
        # the rest of fields will be decided by the setting - UsersRequiredFields
        if self.required_fields_list:
            for field in self.required_fields_list:
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
        params = {'first_name': self.cleaned_data['first_name'],
                  'last_name': self.cleaned_data['last_name'],
                  'email': self.cleaned_data['email'], }
        
        if not self.user_this:
            password = self.cleaned_data['password1']
            new_user = User.objects.create_user(username, email, password)
            self.instance.user = new_user 
            update_user(new_user, **params)            
        else:
            # for update_subscription
            self.instance.old_email = user_edit.email
            
            params.update({'username': username})
            update_user(user_edit, **params) 
            
        if not self.instance.id:
            self.instance.creator = request.user
            self.instance.creator_username = request.user.username
        self.instance.owner = request.user
        self.instance.owner_username = request.user.username
            
        return super(ProfileForm, self).save(*args, **kwargs)


class ProfileAdminForm(TendenciBaseForm):

    first_name = forms.CharField(label=_("First Name"), max_length=100,
                                 error_messages={'required': 'First Name is a required field.'})
    last_name = forms.CharField(label=_("Last Name"), max_length=100,
                                error_messages={'required': 'Last Name is a required field.'})
    email = EmailVerificationField(label=_("Email"),
                                error_messages={'required': 'Email is a required field.'})
    email2 = EmailVerificationField(label=_("Email 2"), required=False)

    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'Username'),
                                help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs=attrs_dict))
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(attrs=attrs_dict),
        help_text = _("Enter the same password as above, for verification."))

    security_level = forms.ChoiceField(initial="user", choices=(('user','User'),
                                                                ('staff','Staff'),
                                                                ('superuser','Superuser'),))
    interactive = forms.ChoiceField(initial=1, choices=((1,'Interactive'),
                                                          (0,'Not Interactive (no login)'),))

    language = forms.ChoiceField(initial="en-us", choices=(('en-us', u'English'),))

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

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
                  'allow_anonymous_view',
                  'admin_notes',
                  'security_level',
                  'status',
                  'status_detail',
                )
        
    def __init__(self, *args, **kwargs):
        super(ProfileAdminForm, self).__init__(*args, **kwargs)
        
        if self.instance.id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].widget.attrs['readonly'] = True
            self.fields['password2'].widget.attrs['readonly'] = True

            if self.instance.user.is_superuser:
                self.fields['security_level'].initial = "superuser"
            elif self.instance.user.is_staff:
                self.fields['security_level'].initial = "staff"
            else:
                self.fields['security_level'].initial = "user"
            if self.instance.user.is_active == 1:
                self.fields['interactive'].initial = 1
            else:
                self.fields['interactive'].initial = 0

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
            if self.instance.id and user.id==self.instance.user.id:
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
        if not self.instance.id:
            if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError(_(u'You must type the same password each time'))
        return self.cleaned_data
        
    def save(self, *args, **kwargs):
        """
        Create a new user then create the user profile
        """
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        params = {'first_name': self.cleaned_data['first_name'],
                  'last_name': self.cleaned_data['last_name'],
                  'email': self.cleaned_data['email'], }
        
        if not self.instance.id:
            password = self.cleaned_data['password1']
            new_user = User.objects.create_user(username, email, password)
            self.instance.user = new_user 
            update_user(new_user, **params)
        else:
            self.instance.old_email = self.instance.user.email
            
            params.update({'username': username})
            update_user(self.instance.user, **params)

        security_level = self.cleaned_data['security_level']
        if security_level == 'superuser':
            self.instance.user.is_superuser = 1
            self.instance.user.is_staff = 1
        elif security_level == 'staff':
            self.instance.user.is_superuser = 0
            self.instance.user.is_staff = 1
        else:
            self.instance.user.is_superuser = 0
            self.instance.user.is_staff = 0

        interactive = self.cleaned_data['interactive']
        try:
            interactive = int(interactive)
        except:
            interactive = 0
        self.instance.user.is_active = interactive

        self.instance.user.save()
            
        return super(ProfileAdminForm, self).save(*args, **kwargs)

        
class UserForm(forms.ModelForm):
    is_superuser = forms.BooleanField(label=_("Is Admin"), 
                                      help_text = _("If selected, this user has all permissions without explicitly assigning them."))
    class Meta:
        model = User
        fields= ('is_superuser', 'user_permissions')


class UserPermissionForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('user_permissions',)

    def __init__(self, *args, **kwargs):
        super(UserPermissionForm, self).__init__(*args, **kwargs)
        # filter out the unwanted permissions,
        # only display the permissions for the apps in APPS
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission
        content_types = ContentType.objects.exclude(app_label='auth')

        self.fields['user_permissions'].queryset = Permission.objects.filter(content_type__in=content_types)


class UserGroupsForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset = Group.objects.all(), required=False)
    
    def __init__(self, user, editor, request, *args, **kwargs):
        self.user = user
        self.editor = editor
        self.request = request
        super(UserGroupsForm, self).__init__(*args, **kwargs)
        self.old_groups = get_groups(self.user, filter=Group.objects.search(user=editor))
        self.old_memberships = get_memberships(self.user, filter=Group.objects.search(user=editor))
        self.fields['groups'].initial = self.old_groups
        self.fields['groups'].choices = group_choices(editor)
        
    def save(self):
        data = self.cleaned_data
        
        #delete old memberships
        for old_m in self.old_memberships:
            if old_m.group not in data['groups']:
                print "membership to %s deleted" % old_m.group
                log_defaults = {
                    'event_id' : 223000,
                    'event_data': '%s (%d) deleted by %s' % (old_m._meta.object_name, old_m.pk, self.editor),
                    'description': '%s deleted' % old_m._meta.object_name,
                    'user': self.editor,
                    'request': self.request,
                    'instance': old_m,
                }
                EventLog.objects.log(**log_defaults)
                old_m.delete()
        
        #create new memberships
        for group in data['groups']:
            try:
                group_membership = GroupMembership.objects.get(group=group, member=self.user)
            except GroupMembership.DoesNotExist:
                group_membership = GroupMembership(group=group, member=self.user)
                group_membership.creator_id = self.editor.id
                group_membership.creator_username = self.editor.username
                
            group_membership.owner_id =  self.editor.id
            group_membership.owner_username = self.editor.username
            
            group_membership.save()
            
            log_defaults = {
                'event_id' : 221000,
                'event_data': '%s (%d) added by %s' % (group_membership._meta.object_name, group_membership.pk, self.editor),
                'description': '%s added' % group_membership._meta.object_name,
                'user': self.editor,
                'request': self.request,
                'instance': group_membership,
            }
            EventLog.objects.log(**log_defaults)

class ValidatingPasswordChangeForm(auth.forms.PasswordChangeForm):
    
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        password_regex = get_setting('module', 'users', 'password_requirements_regex')
        password_requirements = get_setting('module', 'users', 'password_text')
        if password_regex:
            # At least MIN_LENGTH long
            # "^(?=.{8,})(?=.*[0-9=]).*$"
            if not re.match(password_regex, password1):
                raise forms.ValidationError(mark_safe("The new password does not meet the requirements </li><li>%s" % password_requirements))

        return password1

class UserMembershipForm(TendenciBaseForm):
    subscribe_dt = SplitDateTimeField(label=_('Subscribe Date/Time'),
        initial=datetime.datetime.now())
    expire_dt = SplitDateTimeField(label=_('Expire Date/Time'), required=False)
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
        
    class Meta:
        model = Membership
        fields = (
            'user',
            'member_number',
            'membership_type',
            'subscribe_dt',
            'expire_dt',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [
            ('Membership Information', {
                'fields': [
                    'user',
                    'member_number',
                    'membership_type',
                    'subscribe_dt',
                    'expire_dt',
                ],
                'legend': ''
                }),
            ('Permissions', {
                'fields': [
                    'allow_anonymous_view',
                    'user_perms',
                    'member_perms',
                    'group_perms',
                ],
                'classes': ['permissions'],
            }),
            ('Administrator Only', {
                'fields': [
                    'syndicate',
                    'status',
                    'status_detail'], 
                'classes': ['admin-only'],
            })]
            
    def __init__(self, *args, **kwargs):
        super(UserMembershipForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        
class ExportForm(forms.Form):
    passcode = forms.CharField(
                    label=_("Type Your Password"), 
                    widget=forms.PasswordInput(render_value=False))
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ExportForm, self).__init__(*args, **kwargs)
        
    def clean_passcode(self):
        value = self.cleaned_data['passcode']
        if not self.user.check_password(value):
            raise forms.ValidationError(_("Invalid password."))
        return value


class ProfileMergeForm(forms.Form):
    user_list = forms.ModelMultipleChoiceField(queryset=Profile.objects.none(),
                    label=_("Choose the users to merge"),
                    widget=forms.CheckboxSelectMultiple())

    master_record = forms.ModelChoiceField(queryset=Profile.objects.none(),
                        empty_label=None,
                        label=_("Choose the master record of the users you are merging above"),
                        widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('list', None)
        super(ProfileMergeForm, self).__init__(*args, **kwargs)

        queryset = Profile.objects.filter(user__in=choices).order_by('-user__last_login')

        self.fields["master_record"].queryset = queryset
        self.fields["user_list"].queryset = queryset

        if queryset.count() == 2:
            self.fields['user_list'].initial = queryset
