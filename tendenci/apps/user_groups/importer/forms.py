import os

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from user_groups.models import ImportFile

class UploadForm(forms.ModelForm):
    """
    CSV upload form for imports
    """
    file = forms.FileField(label=_("XLS File"), help_text=_('The importer will automatically recognize fields from your XLS spreadsheet. A subscribers First name is found by looking for the word "first" in the heading. "Last" and "full" are also automatically matched. Email fields are matched by finding a valid email address in them. Records without a valid email address will not be imported.'))
    
    class Meta:
        model = ImportFile
        fields = (
            'file',
        )
