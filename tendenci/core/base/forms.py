from re import compile
from django import forms

from django.core.validators import RegexValidator
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField


slug_re = compile(r'^[-\w\/]+$')
validate_slug = RegexValidator(slug_re, _(u"Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens."), 'invalid')

class SlugField(CharField):
    """
        New form slug field that validates with front slashes
        Straight copy from django with modifications
    """
    default_error_messages = {
        'invalid': _(u"Enter a valid 'slug' consisting of letters, numbers,"
                     u" underscores (_), front-slashes (/) or hyphens."),
    }
    default_validators = [validate_slug]
    
    def __init__(self, help_text=None, *args, **kwargs):
        super(SlugField, self).__init__(*args, **kwargs)
        
    def clean(self, value):
        value = self.to_python(value)     
        value = value.replace('//','')
        value = value.strip('/')

        self.validate(value)
        self.run_validators(value)
        
        return value

class PasswordForm(forms.Form):
    password = forms.CharField(label=_(u'Password'),
        widget=forms.PasswordInput())
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(_("Incorrect Password"))
        return self.cleaned_data


class CaptchaForm(forms.Form):
    captcha = CaptchaField(label=_('Type the code below'))