from django import forms
from helpfiles.models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
