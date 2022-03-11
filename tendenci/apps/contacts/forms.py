from django import forms
from django.conf import settings
# from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _

from tendenci.apps.contacts.models import Contact
from tendenci.apps.base.fields import EmailVerificationField, CountrySelectField
from tendenci.apps.base.forms import CustomCatpchaField


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            'first_name',
            'last_name',
            'addresses',
            'phones',
            'emails',
            'urls',
            'companies',
            'message',
        )
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['timezone'].initial = settings.TIME_ZONE

class SubmitContactForm(forms.Form):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)

    address = forms.CharField(max_length=50, required=False)
    city = forms.CharField(max_length=50, required=False)
    state = forms.CharField(max_length=50, required=False)
    zipcode = forms.CharField(max_length=10, required=False)
    country = CountrySelectField(required=False)

    phone = forms.CharField(max_length=20, required=False)
    email = EmailVerificationField(label=_("Email"))
    url = forms.URLField(label=_('URL'), max_length=200, required=False)

    message = forms.CharField(widget=forms.Textarea)
    captcha = CustomCatpchaField(label=_('Type the code below'))
