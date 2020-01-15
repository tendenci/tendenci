import datetime
import re

from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import SelectDateWidget
from django.utils.safestring import mark_safe
from django.db.models import Q

from tendenci.apps.base.fields import EmailVerificationField, CountrySelectField
from tendenci.apps.base.utils import normalize_field_names
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.apps.memberships.models import MembershipDefault
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.profiles.models import Profile, UserImport
from tendenci.apps.profiles.utils import update_user
from tendenci.apps.base.utils import get_languages_with_local_name
from tendenci.apps.perms.utils import get_query_filters

attrs_dict = {'class': 'required' }
THIS_YEAR = datetime.date.today().year
# this is the list of apps whose permissions will be displayed on the permission edit page
APPS = ('profiles', 'user_groups', 'articles',
        'news', 'pages', 'jobs', 'locations',
        'stories', 'actions', 'photos', 'entities',
        'locations', 'files', 'directories', 'resumes',
        'memberships', 'corporate_memberships')


class ProfileSearchForm(forms.Form):
    SEARCH_CRITERIA_CHOICES = (
                        ('', _('SELECT ONE')),
                        ('first_name', _('First Name')),
                        ('last_name', _('Last Name')),
                        ('email', _('Email')),
                        ('username', _('Username')),
                        ('member_number', _('Member Number')),
                        ('company', _('Company')),
                        ('department', _('Department')),
                        ('position_title', _('Position Title')),
                        ('phone', _('Phone')),
                        ('city', _('City')),
                        ('region', _('Region')),
                        ('state', _('State')),
                        ('zipcode', _('Zip Code')),
                        ('country', _('Country')),
                        ('spouse', _('Spouse'))
                        )
    SEARCH_METHOD_CHOICES = (
                             ('starts_with', _('Starts With')),
                             ('contains', _('Contains')),
                             ('exact', _('Exact')),
                             )
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    member_only = forms.BooleanField(label=_('Show Member Only'),
                                     widget=forms.CheckboxInput(),
                                     initial=True, required=False)
    membership_type = forms.IntegerField(required=False)
    group = forms.IntegerField(required=False)
    search_criteria = forms.ChoiceField(choices=SEARCH_CRITERIA_CHOICES,
                                        required=False)
    search_text = forms.CharField(max_length=100, required=False)
    search_method = forms.ChoiceField(choices=SEARCH_METHOD_CHOICES,
                                        required=False)

    def __init__(self, *args, **kwargs):
        mts = kwargs.pop('mts')
        self.user = kwargs.pop('user')
        super(ProfileSearchForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': _('Exact Match Search')})
        self.fields['last_name'].widget.attrs.update({'placeholder': _('Exact Match Search')})
        self.fields['email'].widget.attrs.update({'placeholder': _('Exact Match Search')})

        if not mts:
            del self.fields['membership_type']
            del self.fields['member_only']
        else:
            choices = [(0, _('SELECT ONE'))]
            choices += [(mt.id, mt.name) for mt in mts]
            self.fields['membership_type'].widget = forms.widgets.Select(
                                    choices=choices)

        # group choices
        filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
        group_choices = [(0, _('SELECT ONE'))] + list(Group.objects.filter(
                            status=True, status_detail="active"
                             ).filter(filters).distinct().order_by('name'
                            ).values_list('pk', 'name'))
        self.fields['group'].widget = forms.widgets.Select(
                                    choices=group_choices)


class ProfileForm(TendenciBaseForm):

    first_name = forms.CharField(label=_("First Name"), max_length=30,
                                 error_messages={'required': _('First Name is a required field.')})
    last_name = forms.CharField(label=_("Last Name"), max_length=30,
                                error_messages={'required': _('Last Name is a required field.')})
    email = EmailVerificationField(label=_("Email"),
                                error_messages={'required': _('Email is a required field.')})
    email2 = EmailVerificationField(label=_("Secondary Email"), required=False)

    initials = forms.CharField(label=_("Initial"), max_length=50, required=False,
                               widget=forms.TextInput(attrs={'size':'10'}))
    display_name = forms.CharField(label=_("Display name"), max_length=100, required=False,
                               widget=forms.TextInput(attrs={'size':'30'}))

    url = forms.CharField(label=_("Web Site"), max_length=100, required=False,
                               widget=forms.TextInput(attrs={'size':'40'}))
    company = forms.CharField(label=_("Company"), max_length=100, required=False,
                              error_messages={'required': _('Company is a required field.')},
                               widget=forms.TextInput(attrs={'size':'45'}))
    department = forms.CharField(label=_("Department"), max_length=50, required=False,
                               widget=forms.TextInput(attrs={'size':'35'}))
    address = forms.CharField(label=_("Address"), max_length=150, required=False,
                              error_messages={'required': _('Address is a required field.')},
                               widget=forms.TextInput(attrs={'size':'45'}))
    address2 = forms.CharField(label=_("Address2"), max_length=100, required=False,
                               widget=forms.TextInput(attrs={'size':'40'}))
    city = forms.CharField(label=_("City"), max_length=50, required=False,
                           error_messages={'required': _('City is a required field.')},
                               widget=forms.TextInput(attrs={'size':'15'}))
    state = forms.CharField(label=_("State"), max_length=50, required=False,
                            error_messages={'required': _('State is a required field.')},
                               widget=forms.TextInput(attrs={'size':'5'}))
    zipcode = forms.CharField(label=_("Zipcode"), max_length=50, required=False,
                              error_messages={'required': _('Zipcode is a required field.')},
                               widget=forms.TextInput(attrs={'size':'10'}))
    country = CountrySelectField(label=_("Country"), required=False)

    address_2 = forms.CharField(label=_("Address"), max_length=64, required=False,
                               widget=forms.TextInput(attrs={'size':'45'}))
    address2_2 = forms.CharField(label=_("Address2"), max_length=64, required=False,
                               widget=forms.TextInput(attrs={'size':'40'}))
    city_2 = forms.CharField(label=_("City"), max_length=35, required=False,
                               widget=forms.TextInput(attrs={'size':'15'}))
    state_2 = forms.CharField(label=_("State"), max_length=35, required=False,
                               widget=forms.TextInput(attrs={'size':'5'}))
    zipcode_2 = forms.CharField(label=_("Zipcode"), max_length=16, required=False,
                               widget=forms.TextInput(attrs={'size':'10'}))
    country_2 = CountrySelectField(label=_("Country"), required=False)

    mailing_name = forms.CharField(label=_("Mailing Name"), max_length=120, required=False,
                                   error_messages={'required': _('Mailing name is a required field.')},
                               widget=forms.TextInput(attrs={'size':'30'}))

    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'Username'),
                                help_text = _("Required. Allowed characters are letters, digits, at sign (@), period (.), plus sign (+), dash (-), and underscore (_)."),
                                error_messages={
                                    'invalid': _('Allowed characters are letters, digits, at sign (@), period (.), plus sign (+), dash (-), and underscore (_).')
                                })

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs=attrs_dict))
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(attrs=attrs_dict),
        help_text = _("Enter the same password as above, for verification."))
    security_level = forms.ChoiceField(initial="user", choices=(('user',_('User')),
                                                                ('staff',_('Staff')),
                                                                ('superuser',_('Superuser')),))
    interactive = forms.ChoiceField(initial=1, choices=((1,'Interactive'),
                                                          (0,_('Not Interactive (no login)')),))
    direct_mail =  forms.ChoiceField(initial=True, choices=((True, _('Yes')),(False, _('No')),))
    notes = forms.CharField(label=_("Notes"), max_length=1000, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    admin_notes = forms.CharField(label=_("Admin Notes"), max_length=1000, required=False,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    language = forms.ChoiceField(initial="en", choices=get_languages_with_local_name())
    dob = forms.DateField(required=False, widget=SelectDateWidget(None, list(range(1920, THIS_YEAR))))

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

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
                  'is_billing_address',
                  'address_2',
                  'address2_2',
                  'city_2',
                  'state_2',
                  'zipcode_2',
                  'county_2',
                  'country_2',
                  'is_billing_address_2',
                  'url',
                  'dob',
                  'ssn',
                  'spouse',
                  'time_zone',
                  'language',
                  'department',
                  'education',
                  'student',
                  'direct_mail',
                  'linkedin',
                  'facebook',
                  'twitter',
                  'instagram',
                  'youtube',
                  'notes',
                  'interactive',
                  'allow_anonymous_view',
                  'admin_notes',
                  'security_level',
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
                del self.fields['status_detail']

            if self.user_current.profile.is_superuser and self.user_current == self.user_this:
                self.fields['security_level'].choices = (('superuser',_('Superuser')),)

        if not self.user_current.profile.is_superuser:
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
            user = User.objects.get(username=self.cleaned_data['username'])
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
                                 error_messages={'required': _('First Name is a required field.')})
    last_name = forms.CharField(label=_("Last Name"), max_length=100,
                                error_messages={'required': _('Last Name is a required field.')})
    email = EmailVerificationField(label=_("Email"),
                                error_messages={'required': _('Email is a required field.')})
    email2 = EmailVerificationField(label=_("Secondary Email"), required=False)

    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'Username'),
                                help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs=attrs_dict))
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(attrs=attrs_dict),
        help_text = _("Enter the same password as above, for verification."))

    security_level = forms.ChoiceField(initial="user", choices=(('user',_('User')),
                                                                ('staff',_('Staff')),
                                                                ('superuser',_('Superuser')),))
    interactive = forms.ChoiceField(initial=1, choices=((1,'Interactive'),
                                                          (0,_('Not Interactive (no login)')),))

    language = forms.ChoiceField(initial="en", choices=get_languages_with_local_name())

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

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
                  'address_2',
                  'address2_2',
                  'city_2',
                  'state_2',
                  'zipcode_2',
                  'county_2',
                  'country_2',
                  'url',
                  'dob',
                  'ssn',
                  'spouse',
                  'time_zone',
                  'language',
                  'department',
                  'education',
                  'student',
                  'direct_mail',
                  'notes',
                  'interactive',
                  'allow_anonymous_view',
                  'admin_notes',
                  'security_level',
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
        request = kwargs.pop('request', None)
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

        if not (request.user == self.instance.user and request.user.is_superuser):
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

        if not self.instance.id:
            self.instance.creator = request.user
            self.instance.creator_username = request.user.username
        self.instance.owner = request.user
        self.instance.owner_username = request.user.username

        self.instance.user.save()
        self.instance.save()

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
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(
                                        ).exclude(type__in=['system_generated', 'membership']),
                                            required=False)

    def __init__(self, user, editor, request, *args, **kwargs):
        self.user = user
        self.editor = editor
        self.request = request
        super(UserGroupsForm, self).__init__(*args, **kwargs)

        self.fields['groups'].initial = self.fields['groups'].queryset.filter(members__in=[self.user])

        if not self.editor.is_superuser:
            queryset = self.fields['groups'].queryset
            queryset = queryset.filter(show_as_option=True, allow_self_add=True)
            if self.editor.profile.is_member:
                queryset = queryset.filter(Q(allow_anonymous_view=True)
                                           | Q(allow_user_view=True)
                                           | Q(allow_member_view=True))
            else:
                queryset = queryset.filter(Q(allow_anonymous_view=True)
                                           | Q(allow_user_view=True))
            self.fields['groups'].queryset = queryset

    def save(self):
        data = self.cleaned_data

        #delete old memberships
        old_memberships = GroupMembership.objects.filter(member=self.user
                                ).exclude(group__type__in=['system_generated', 'membership'])
        if not self.editor.is_superuser:
            old_memberships = old_memberships.filter(group__show_as_option=True,
                                                     group__allow_self_remove=True)
            if self.editor.profile.is_member:
                old_memberships = old_memberships.filter(Q(group__allow_anonymous_view=True)
                                           | Q(group__allow_user_view=True)
                                           | Q(group__allow_member_view=True))
            else:
                old_memberships = old_memberships.filter(Q(group__allow_anonymous_view=True)
                                           | Q(group__allow_user_view=True))

        for old_m in old_memberships:
            if old_m.group not in data['groups']:
                #print("membership to %s deleted" % old_m.group)
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
            [group_membership] = GroupMembership.objects.filter(group=group, member=self.user)[:1] or [None]
            if not group_membership:
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
    def __init__(self, user, *args, **kwargs):
        super(ValidatingPasswordChangeForm, self).__init__(user, *args, **kwargs)

        self.fields['old_password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        password_regex = get_setting('module', 'users', 'password_requirements_regex')
        password_requirements = get_setting('module', 'users', 'password_text')
        if password_regex:
            # At least MIN_LENGTH long
            # r'^(?=.{8,})(?=.*[0-9=]).*$'
            if not re.match(password_regex, password1):
                raise forms.ValidationError(mark_safe("The new password does not meet the requirements </li><li>%s" % password_requirements))

        return password1


class UserMembershipForm(TendenciBaseForm):
    join_dt = forms.SplitDateTimeField(label=_('Subscribe Date/Time'),
        initial=datetime.datetime.now())
    expire_dt = forms.SplitDateTimeField(label=_('Expire Date/Time'), required=False)
    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

    class Meta:
        model = MembershipDefault
        fields = (
            'member_number',
            'membership_type',
            'join_dt',
            'expire_dt',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [
            (_('Membership Information'), {
                'fields': [
                    'member_number',
                    'membership_type',
                    'join_dt',
                    'expire_dt',
                ],
                'legend': ''
                }),
            (_('Permissions'), {
                'fields': [
                    'allow_anonymous_view',
                    'user_perms',
                    'member_perms',
                    'group_perms',
                ],
                'classes': ['permissions'],
            }),
            (_('Administrator Only'), {
                'fields': [
                    'status',
                    'status_detail'],
                'classes': ['admin-only'],
            })]

    def __init__(self, *args, **kwargs):
        super(UserMembershipForm, self).__init__(*args, **kwargs)


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


class ExportForm(forms.Form):

    EXPORT_FIELD_CHOICES = (
        ('main_fields', _('Export Main Fields (fastest)')),
        ('all_fields', _('Export All Fields')),
    )

    export_format = forms.CharField(widget=forms.HiddenInput(), initial='csv')
    export_fields = forms.ChoiceField(choices=EXPORT_FIELD_CHOICES)


class UserUploadForm(forms.ModelForm):
    KEY_CHOICES = (('email', _('Email')),
               ('first_name,last_name,email', _('First Name and Last Name and Email')),
               ('first_name,last_name,phone', _('First Name and Last Name and Phone')),
               ('first_name,last_name,company', _('First Name and Last Name and Company')),
               ('username', 'Username'),)

    interactive = forms.BooleanField(widget=forms.RadioSelect(
                                    choices=UserImport.INTERACTIVE_CHOICES),
                                    initial=False, required=False)
    key = forms.ChoiceField(label="Key",
                            choices=KEY_CHOICES)
    group_id = forms.ChoiceField(label=_("Add Users to Group"),
                            required=False)
    clear_group_membership = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = UserImport
        fields = (
                'key',
                'override',
                'interactive',
                'group_id',
                'clear_group_membership',
                'upload_file',
                  )

    def __init__(self, *args, **kwargs):
        super(UserUploadForm, self).__init__(*args, **kwargs)
        self.fields['key'].initial = 'email'
        # move the choices down here to fix the error
        #  django.db.utils.ProgrammingError: relation "user_groups_group" does not exist
        GROUP_CHOICES = [(0, _('Select One'))] + [(group.id, group.name) for group in
                     Group.objects.filter(status=True, status_detail='active'
                                          ).exclude(type='membership')]
        self.fields['group_id'].choices = GROUP_CHOICES

    def clean_upload_file(self):
        key = self.cleaned_data['key']
        upload_file = self.cleaned_data['upload_file']
        if not key:
            raise forms.ValidationError(_('Please specify the key to identify duplicates'))

        file_content = upload_file.read().decode('utf-8') # decode from bytes to string
        upload_file.seek(0)
        header_line_index = file_content.find('\n')
        header_list = ((file_content[:header_line_index]
                            ).strip('\r')).split(',')
        header_list = normalize_field_names(header_list)
        key_list = []
        for key in key.split(','):
            key_list.append(key)
        missing_columns = []
        for item in key_list:
            if item not in header_list:
                missing_columns.append(item)
        if missing_columns:
            raise forms.ValidationError(_(
                        """
                        'Field(s) %(fields)s used to identify the duplicates
                        should be included in the .csv file.'
                        """ % {'fields' : ', '.join(missing_columns)}))

        return upload_file


class ActivateForm(forms.Form):
    email = forms.CharField(max_length=75)
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30, required=False)
