import os

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from user_groups.models import ImportFile

class UploadForm(forms.ModelForm):
    """
    CSV upload form for imports
    """
    file = forms.FileField(label=_("CSV File"))
    
    class Meta:
        model = ImportFile
        fields = (
            'file',
        )
