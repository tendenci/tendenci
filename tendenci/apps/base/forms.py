from re import compile
import zipfile

from django import forms

from django.core.validators import RegexValidator
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField, CaptchaTextInput
SIMPLE_ANSWER = 22
SIMPLE_QUESTION = _('What is 9 + 13? (security question -just so we know you\'re not a bot)')

slug_re = compile(r'^[-\w\/]+$')
validate_slug = RegexValidator(slug_re, _(u"Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens."), 'invalid')


class FormControlWidgetMixin(object):
    """
    Mixin that adds 'form-control' class to all fields of a form

    """

    def __init__(self, *args, **kwargs):
        super(FormControlWidgetMixin, self).__init__(*args, **kwargs)

        self.add_form_control_class()

    def add_form_control_class(self):

        # Add .'form-control' class to all field widgets
        for field_name in self.fields.keys():

            #print '%s: %s' % (field_name, self.fields[field_name].widget.__class__.__name__.lower(),)
            non_form_control_widgets = [
                'checkboxinput', 'radioselect', 'checkboxselectmultiple',
                'userpermissionwidget', 'grouppermissionwidget', 'memberpermissionwidget',
            ]
            if self.fields[field_name].widget.__class__.__name__.lower() not in non_form_control_widgets:
                widget_attrs = self.fields[field_name].widget.attrs

                class_attr = 'form-control'
                if 'class' in widget_attrs.keys():
                    class_attr = widget_attrs['class']

                    if 'form-control' not in class_attr:
                        class_attr = class_attr + ' form-control'

                self.fields[field_name].widget.attrs.update({'class': class_attr})


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

class SimpleMathField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['required'] = True
        kwargs['label'] = SIMPLE_QUESTION
        super(SimpleMathField, self).__init__((), *args, **kwargs)

    def clean(self, value):
        try:
            value = int(value)
        except:
            value = 0
        if value != SIMPLE_ANSWER:
            raise forms.ValidationError(_("Incorrect. Please try again."))

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


class CaptchaForm(FormControlWidgetMixin, forms.Form):
    captcha = CaptchaField(label=_('Type the code below'))


class AddonUploadForm(forms.Form):
    addon = forms.FileField(label=_(u'File'),
                           help_text=_("Enter the zip file of the module."))

    def clean_addon(self):
        addon = self.cleaned_data['addon']
        try:
            zip_file = zipfile.ZipFile(addon)
        except:
            raise forms.ValidationError(_("Could not unzip file."))
        bad_file = zip_file.testzip()
        zip_file.close()
        del zip_file
        if bad_file:
            raise forms.ValidationError(_('Bad file/s found in ZIP archive.'))
        return addon
