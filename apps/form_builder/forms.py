from django import forms
from contacts.models import Contact
from captcha.fields import CaptchaField
from django.utils.translation import ugettext_lazy as _ 

class ContactForm(forms.Form):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)

    address = forms.CharField(max_length=50, required=False)
    city = forms.CharField(max_length=50, required=False)
    state = forms.CharField(max_length=50, required=False)
    zipcode = forms.CharField(max_length=10, required=False)
    country = forms.CharField(max_length=100, required=False)

    phone = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(max_length=100)
    url = forms.URLField(label=_('URL'), max_length=200, required=False)

    message = forms.CharField(widget=forms.Textarea)
    captcha = CaptchaField()