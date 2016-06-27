import re

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.safestring import mark_safe
from django.contrib.auth.tokens import default_token_generator
from django.template import Context, loader
from django.utils.http import int_to_base36
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from captcha.fields import CaptchaField, CaptchaTextInput
from tendenci.apps.registration.forms import RegistrationForm
from tendenci.apps.profiles.models import Profile
from tendenci.apps.registration.models import RegistrationProfile
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.accounts.utils import send_registration_activation_email
from tendenci.apps.base.utils import create_salesforce_contact


class SetPasswordCustomForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordCustomForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        password_regex = get_setting('module', 'users', 'password_requirements_regex')
        password_requirements = get_setting('module', 'users', 'password_text')
        if password_regex:
            if not re.match(password_regex, new_password1):
                raise forms.ValidationError(mark_safe("The password does not meet the requirements: %s" % password_requirements))

        return new_password1


class RegistrationCustomForm(RegistrationForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    company = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':'40', 'class': 'form-control'}), required=False)
    phone = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'size':'40', 'class': 'form-control'}), required=False)
    city = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'size':'10', 'class': 'form-control'}), required=False)
    country = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    zipcode = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label=_('Type the letters you see in the box'), widget=CaptchaTextInput(attrs={'class': 'form-control'}))

    allow_same_email = None
    similar_email_found = False

    def __init__(self, *args, **kwargs):
        self.allow_same_email = kwargs.pop('allow_same_email', False)

        super(RegistrationCustomForm, self).__init__(*args, **kwargs)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        password_regex = get_setting('module', 'users', 'password_requirements_regex')
        password_requirements = get_setting('module', 'users', 'password_text')
        if password_regex:
            if not re.match(password_regex, password1):
                raise forms.ValidationError(mark_safe(_("The password does not meet the requirements: %(p)s" % {'p': password_requirements })))

        return password1

    def clean(self):
        if self._errors:
            return
        user = User.objects.filter(email=self.cleaned_data['email'])
        if user and not self.allow_same_email:
            self.similar_email_found = True
            raise forms.ValidationError(_("Similar emails found"))

        return self.cleaned_data


    def save(self, profile_callback=None, event=None):
        #
        #new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
        #                                                            password=self.cleaned_data['password1'],
        # create inactive user                                                           email=self.cleaned_data['email'])
        new_user = User.objects.create_user(self.cleaned_data['username'],
                                            self.cleaned_data['email'],
                                            self.cleaned_data['password1'])

        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.is_active = False
        new_user.save()
        # create registration profile
        registration_profile = RegistrationProfile.objects.create_profile(new_user)
        send_registration_activation_email(new_user, registration_profile, event=event)

        new_profile = Profile(user=new_user,
                              company=self.cleaned_data['company'],
                              phone=self.cleaned_data['phone'],
                              address=self.cleaned_data['address'],
                              city=self.cleaned_data['city'],
                              state=self.cleaned_data['state'],
                              country=self.cleaned_data['country'],
                              zipcode=self.cleaned_data['zipcode'],
                              )
        user_hide_default = get_setting('module', 'users', 'usershidedefault')
        if user_hide_default:
            new_profile.hide_in_search = 1
            new_profile.hide_address = 1
            new_profile.hide_email = 1
            new_profile.hide_phone = 1

        new_profile.creator = new_user
        new_profile.creator_username = new_user.username
        new_profile.owner = new_user
        new_profile.owner_username = new_user.username
        new_profile.save()
        sf_id = create_salesforce_contact(new_profile)

        return new_user


class LoginForm(forms.Form):

    username = forms.CharField(label=_("Username"), max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control'}))
    #remember = forms.BooleanField(label=_("Remember Me"), help_text=_("If checked you will stay logged in for 3 weeks"), required=False)
    remember = forms.BooleanField(label=_("Remember Login"), required=False)

    user_exists = None
    user = None

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # check if we need to hide the remember me checkbox
        # and set the default value for remember me
        hide_remember_me = get_setting('module', 'users', 'usershiderememberme')
        remember_me_default_checked = get_setting('module', 'users', 'usersremembermedefaultchecked')

        if remember_me_default_checked:
            self.fields['remember'].initial = True
        if hide_remember_me:
            self.fields['remember'].widget = forms.HiddenInput()

    def clean(self):
        if self._errors:
            return
        #invalidate('auth_user')
        user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])

        if user:
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile.objects.create_profile(user=user)

            if user.is_active and profile.status == True and profile.status_detail.lower() == 'active':
                self.user = user
            else:
                raise forms.ValidationError(_("This account is currently inactive."))
        else:
            try:
                self.user_exists = User.objects.get(username=self.cleaned_data["username"])
                raise forms.ValidationError(_("The username and/or password you specified are not correct."))
            except User.DoesNotExist:
                raise forms.ValidationError(_("The username and/or password you specified are not correct."))
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            login(request, self.user)

            messages.add_message(
                request, messages.SUCCESS,
                _(u"Hello %(first_name)s %(last_name)s, you've successfully logged in." % {
                    'first_name' : self.user.first_name or self.user.username,
                    'last_name' : self.user.last_name }))

            if self.cleaned_data['remember']:
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                request.session.set_expiry(0)
            return True
        return False

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        """
        Validates that a user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self_reg = get_setting('module', 'users', 'selfregistration')
        self.email = email
        self.users_cache = User.objects.filter(email__iexact=email, is_active=True)
        if len(self.users_cache) == 0:
            if self_reg:
                raise forms.ValidationError(mark_safe(_('That e-mail address doesn\'t have an associated user account. Are you sure you\'ve <a href="/accounts/register" >registered</a>?')))
            else:
                raise forms.ValidationError(_("That e-mail address doesn't have an associated user account."))
        return email

    def save(self, email_template_name='registration/password_reset_email_user_list.html', **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the designated email.
        The email will contain links for resetting passwords for all accounts associated to the email.
        """
        from django.core.mail import send_mail

        email_template_name = 'registration/password_reset_email_user_list.html'

        domain_override = kwargs.get('domain_override', False)
        use_https = kwargs.get('use_https', False)
        token_generator = kwargs.get('token_generator', default_token_generator)

        user_list = []
        for user in self.users_cache:
            user_list.append({
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': token_generator.make_token(user),
                })
        if not domain_override:
            site_name = get_setting('site', 'global', 'sitedisplayname')
        else:
            site_name = domain_override
        site_url = get_setting('site', 'global', 'siteurl')
        t = loader.get_template(email_template_name)
        c = {
            'email': self.email,
            'site_url': site_url,
            'site_name': site_name,
            'user_list': user_list,
            'protocol': use_https and 'https' or 'http',
        }

        from_email = get_setting('site', 'global', 'siteemailnoreplyaddress') or settings.DEFAULT_FROM_EMAIL
        send_mail(_("Password reset on %s") % site_name,
            t.render(Context(c)), from_email, [user.email])
