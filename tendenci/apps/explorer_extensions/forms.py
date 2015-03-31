from django import forms
from tendenci.apps.explorer_extensions.models import DatabaseDumpFile
from django.utils.translation import ugettext_lazy as _


class DatabaseDumpForm(forms.Form):
    format = forms.ChoiceField(choices=DatabaseDumpFile.FORMAT_CHOICES)
