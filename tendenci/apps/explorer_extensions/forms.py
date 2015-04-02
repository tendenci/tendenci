from django import forms
from tendenci.apps.explorer_extensions.models import DatabaseDumpFile
from django.utils.translation import ugettext_lazy as _


class DatabaseDumpForm(forms.Form):
    format = forms.ChoiceField(choices=DatabaseDumpFile.FORMAT_CHOICES)

    def __init__(self, *args, **kwargs):
        super(DatabaseDumpForm, self).__init__(*args, **kwargs)
        self.fields['format'].widget.attrs['class'] = 'form-control'
